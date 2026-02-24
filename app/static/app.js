// core.js will initialize Vue functions, api, and appState before this runs


// Components are defined in separate files and globally available (DashboardView, BookingsView, etc.)


// ══════════════════════════════════════════════════════════════
// Routing
// ══════════════════════════════════════════════════════════════
const routes = [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: DashboardView, name: 'dashboard' },
    { path: '/bookings', component: BookingsView, name: 'bookings' },
    { path: '/bookings/:id', component: BookingDetailView, name: 'bookingDetail' },
    { path: '/employees', component: EmployeesView, name: 'employees' },
    { path: '/employees/:id', component: EmployeeDetailView, name: 'employeeDetail' },
    { path: '/companies', component: CompaniesView, name: 'companies' },
    { path: '/companies/:id', component: CompanyDetailView, name: 'companyDetail' },
    { path: '/calendar', component: CalendarView, name: 'calendar' },
    { path: '/tracker', component: TrackerView, name: 'tracker' },
    { path: '/reports', component: ReportsView, name: 'reports' },
    { path: '/export', component: ExportView, name: 'export' },
    { path: '/settings', component: SettingsView, name: 'settings' },
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes,
});

// ══════════════════════════════════════════════════════════════
// Main Vue App
// ══════════════════════════════════════════════════════════════
const app = createApp({
    setup() {
        const route = VueRouter.useRoute();
        const routeName = computed(() => route.name || '');

        // Helper to ping python script to seed UI (temporary endpoint mock if not available)
        const resetDb = async () => {
            if (confirm('Are you sure you want to reset the database? All data will be lost.')) {
                try {
                    await api.request('/api/admin/reset-db', { method: 'POST' });
                    appState.showToast('Database reset successfully.');
                    window.location.reload();
                } catch (e) { }
            }
        };

        const isDarkMode = ref(localStorage.getItem('theme') === 'dark');
        const toggleDarkMode = () => {
            isDarkMode.value = !isDarkMode.value;
            localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
            document.documentElement.classList.toggle('dark', isDarkMode.value);
        };

        const seedDb = async () => {
            if (!confirm('Seed demo data into database?')) return;
            const resetFirst = confirm('Reset DB before seeding? Click Cancel to append sample data only.');
            try {
                await api.request(`/api/admin/seed-db?reset_first=${resetFirst}`, { method: 'POST' });
                appState.showToast('Database seeded successfully.');
                window.location.reload();
            } catch (e) { }
        };

        // Global Search State
        const globalSearchQuery = ref('');
        const showGlobalSearch = ref(false);
        const isGlobalSearching = ref(false);
        const globalSearchResults = reactive({ companies: [], employees: [], bookings: [] });
        const __router = VueRouter.useRouter();

        let _searchTimeout = null;
        const debouncedGlobalSearch = () => {
            clearTimeout(_searchTimeout);
            if (globalSearchQuery.value.length < 2) {
                globalSearchResults.companies = [];
                globalSearchResults.employees = [];
                globalSearchResults.bookings = [];
                return;
            }
            _searchTimeout = setTimeout(async () => {
                isGlobalSearching.value = true;
                try {
                    const res = await api.request(`/api/search/search?q=${encodeURIComponent(globalSearchQuery.value)}`);
                    globalSearchResults.companies = res.companies || [];
                    globalSearchResults.employees = res.employees || [];
                    globalSearchResults.bookings = res.bookings || [];
                } catch (e) { }
                finally { isGlobalSearching.value = false; }
            }, 300);
        };

        const hideGlobalSearch = () => {
            setTimeout(() => { showGlobalSearch.value = false; }, 200);
        };

        const goToDetail = (type, id) => {
            showGlobalSearch.value = false;
            globalSearchQuery.value = '';
            __router.push(`/${type}/${id}`);
        };

        // Keyboard shortcut CMD/CTRL + K
        onMounted(() => {
            document.documentElement.classList.toggle('dark', isDarkMode.value);
            const handleKeydown = (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    const searchInput = document.querySelector('input[placeholder="Search everywhere..."]');
                    if (searchInput) searchInput.focus();
                }
            };
            window.addEventListener('keydown', handleKeydown);
            // onUnmounted isn't top-level imported but we can just leave listener since it's global SPA anyway
        });

        // Notifications State
        const notifications = reactive({
            alerts: [],
            unread_count: 0
        });
        const showNotifications = ref(false);

        const fetchNotifications = async () => {
            try {
                const res = await api.request('/api/search/notifications');
                notifications.alerts = res.alerts;
                notifications.unread_count = res.unread_count;
            } catch (e) {
                console.error("Failed to load notifications", e);
            }
        };

        const hideNotifications = () => {
            setTimeout(() => { showNotifications.value = false; }, 200);
        };

        const goToRoute = (path) => {
            showNotifications.value = false;
            router.push(path);
        };

        // WebSocket for Real-Time Updates
        let ws = null;
        const initWebSocket = () => {
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'booking_created') {
                        appState.showToast(`New booking incoming: ${data.id}`, 'success');
                    } else if (data.type === 'booking_updated' || data.type === 'status_updated') {
                        appState.showToast(`Active booking updated: ${data.id}`, 'info');
                    } else if (data.type === 'booking_deleted') {
                        appState.showToast(`Booking removed: ${data.id}`, 'error');
                    }
                    // Dispatch global event so components can refresh
                    window.dispatchEvent(new CustomEvent('realtime-update', { detail: data }));
                } catch (e) { }
            };

            ws.onclose = () => {
                setTimeout(initWebSocket, 5000);
            };
        };

        const loginForm = reactive({ username: '', password: '', loading: false });

        const handleLogin = async () => {
            loginForm.loading = true;
            try {
                const fd = new FormData();
                fd.append("username", loginForm.username);
                fd.append("password", loginForm.password);
                const res = await fetch('/api/v1/auth/login', { method: 'POST', body: fd });
                if (!res.ok) throw new Error("Invalid credentials");
                const data = await res.json();
                appState.login(data.access_token);
                appState.showToast("Logged in successfully");
            } catch (err) {
                appState.showToast(err.message, 'error');
            } finally {
                loginForm.loading = false;
            }
        };

        const logout = () => appState.logout();

        onMounted(() => {
            initWebSocket();
            fetchNotifications();
            window.addEventListener('realtime-update', fetchNotifications);
        });

        onUnmounted(() => {
            window.removeEventListener('realtime-update', fetchNotifications);
        });

        return {
            isAuthenticated: computed(() => appState.isAuthenticated),
            loginForm, handleLogin, logout,
            routeName,
            toasts: computed(() => appState.toasts),
            removeToast: (id) => appState.removeToast(id),
            resetDb,
            seedDb,
            globalSearchQuery,
            showGlobalSearch,
            isGlobalSearching,
            globalSearchResults,
            debouncedGlobalSearch,
            hideGlobalSearch,
            goToDetail,
            isDarkMode,
            toggleDarkMode,
            notifications,
            showNotifications,
            hideNotifications,
            goToRoute
        };
    }
});

app.use(router);

app.directive('click-outside', clickOutsideDirective);
app.component('autocomplete-input', AutocompleteInput);

app.mount('#app');
