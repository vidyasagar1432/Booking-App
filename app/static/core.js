const { createApp, ref, reactive, onMounted, onUnmounted, computed, watch, defineComponent } = Vue;

// ══════════════════════════════════════════════════════════════
// Global State & Toasts
// ══════════════════════════════════════════════════════════════
const appState = reactive({
    toasts: [],
    toastIdPrefix: 0,
    token: localStorage.getItem('auth_token') || 'bypass-token',
    isAuthenticated: true,
    showToast(message, type = 'success') {
        const id = ++this.toastIdPrefix;
        this.toasts.push({ id, message, type });
        setTimeout(() => { this.removeToast(id); }, 4000);
    },
    removeToast(id) {
        const index = this.toasts.findIndex(t => t.id === id);
        if (index > -1) this.toasts.splice(index, 1);
    },
    login(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    },
    logout() {
        this.token = null;
        localStorage.removeItem('auth_token');
        window.location.reload();
    }
});

Object.defineProperty(appState, 'isAuthenticated', {
    get: function () { return true; }
});

// ══════════════════════════════════════════════════════════════
// HTTP Client Utility
// ══════════════════════════════════════════════════════════════
const api = {
    async request(url, options = {}) {
        if (url.startsWith('/api/') && !url.startsWith('/api/v1/')) {
            url = '/api/v1' + url.substring(4);
        }

        const headers = options.headers || {};
        // Use a dummy token if none exists to satisfy any potential backend checks, though they were removed
        const token = appState.token || 'bypass-token';
        headers['Authorization'] = `Bearer ${token}`;
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = headers['Content-Type'] || 'application/json';
        }
        const mergedOptions = { ...options, headers };

        if (mergedOptions.body && typeof mergedOptions.body === 'object' && !(mergedOptions.body instanceof FormData)) {
            mergedOptions.body = JSON.stringify(mergedOptions.body);
        }

        try {
            const response = await fetch(url, mergedOptions);

            if (response.status === 401) {
                appState.logout();
                throw new Error("Session expired. Please log in again.");
            }

            if (options.responseType === 'blob') {
                if (!response.ok) throw new Error('Failed to download file');
                return await response.blob();
            }

            const contentType = response.headers.get('content-type');
            let data = null;
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            }
            if (!response.ok) {
                throw new Error(data?.detail || response.statusText || 'Something went wrong');
            }
            return data;
        } catch (error) {
            appState.showToast(error.message, 'error');
            throw error;
        }
    }
};

// ══════════════════════════════════════════════════════════════
// Directives & Shared Components
// ══════════════════════════════════════════════════════════════

const clickOutsideDirective = {
    mounted(el, binding) {
        el.clickOutsideEvent = function (event) {
            if (!(el === event.target || el.contains(event.target))) {
                binding.value(event, el);
            }
        };
        document.body.addEventListener('mousedown', el.clickOutsideEvent);
    },
    unmounted(el) {
        document.body.removeEventListener('mousedown', el.clickOutsideEvent);
    }
};

const AutocompleteInput = defineComponent({
    props: {
        modelValue: { type: String, default: '' },
        field: { type: String, required: true },
        placeholder: { type: String, default: '' },
        required: { type: Boolean, default: false },
        inputClass: { type: String, default: 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 text-sm placeholder-gray-400 bg-white' }
    },
    emits: ['update:modelValue', 'select'],
    template: `
        <div class="relative w-full" :class="{ 'z-[60]': isOpen }" v-click-outside="closeSuggestions">
            <input type="text"
                   :value="modelValue"
                   @input="onInput"
                   @focus="onFocus"
                   :placeholder="placeholder"
                   :required="required"
                   autocomplete="off"
                   :class="inputClass">
            <div v-show="isOpen && suggestions.length > 0" class="absolute z-[100] w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-2xl max-h-44 overflow-y-auto ring-1 ring-black/5 animate-fade-in group-focus-within:visible">
                <ul class="py-1.5 divide-y divide-gray-50">
                    <li v-for="(sug, index) in suggestions" :key="index"
                        @mousedown.prevent="selectSuggestion(sug)"
                        class="px-4 py-2.5 hover:bg-brand-50 cursor-pointer text-sm font-medium text-gray-700 transition-colors flex items-center gap-2">
                        <i class='bx bx-user text-gray-300 text-base'></i>
                        <span class="truncate">{{ sug }}</span>
                    </li>
                </ul>
            </div>
        </div>
    `,
    setup(props, { emit }) {
        const isOpen = ref(false);
        const isFocused = ref(false);
        const suggestions = ref([]);
        let timeout = null;

        const fetchSuggestions = async (q) => {
            if (!q || q.length < 1) {
                suggestions.value = [];
                isOpen.value = false;
                return;
            }
            try {
                const res = await api.request('/api/search/suggestions/' + props.field + '?q=' + encodeURIComponent(q));
                suggestions.value = res;
                // Only open if the input still has focus
                if (isFocused.value) {
                    isOpen.value = res.length > 0;
                }
            } catch (e) {
                console.error('Failed to fetch suggestions', e);
            }
        };

        const onInput = (e) => {
            const val = e.target.value;
            emit('update:modelValue', val);
            clearTimeout(timeout);
            timeout = setTimeout(() => fetchSuggestions(val), 300);
        };

        const onFocus = () => {
            isFocused.value = true;
            if (props.modelValue && suggestions.value.length > 0) {
                isOpen.value = true;
            } else if (props.modelValue && props.modelValue.length > 0) {
                fetchSuggestions(props.modelValue);
            }
        };

        const selectSuggestion = (sug) => {
            clearTimeout(timeout);
            emit('update:modelValue', sug);
            emit('select', sug);
            isOpen.value = false;
        };

        const closeSuggestions = () => {
            isOpen.value = false;
            isFocused.value = false;
        };

        onUnmounted(() => clearTimeout(timeout));

        return { isOpen, suggestions, onInput, onFocus, selectSuggestion, closeSuggestions };
    }
});
