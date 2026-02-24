const SettingsView = defineComponent({
    template: `
        <div class="max-w-4xl mx-auto space-y-6">
            <div class="premium-card p-6 md:p-8 rounded-3xl relative overflow-hidden shrink-0 border border-gray-100 dark:border-gray-800 shadow-sm animate-fade-in">
                <div class="absolute inset-y-0 right-0 w-32 bg-gray-100/50 dark:bg-gray-800/30 rounded-l-full -z-10 blur-2xl"></div>
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-black text-gray-900 leading-tight">System Settings</h2>
                        <p class="text-xs text-gray-500 font-medium tracking-wide mt-1">Configure global application parameters and tenant defaults.</p>
                    </div>
                    <div class="w-12 h-12 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center text-gray-400">
                        <i class='bx bx-cog text-3xl animate-[spin_4s_linear_infinite]'></i>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Navigation Sidebar for Settings (future expansion) -->
                <div class="space-y-2">
                    <button class="w-full text-left px-4 py-3 rounded-xl font-bold text-sm bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400 border border-brand-100 dark:border-brand-800 transition-colors">
                        <i class='bx bx-abacus mr-2'></i> General Preferences
                    </button>
                    <button class="w-full text-left px-4 py-3 rounded-xl font-semibold text-sm text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                        <i class='bx bx-lock-alt mr-2'></i> Security & Access
                    </button>
                    <button class="w-full text-left px-4 py-3 rounded-xl font-semibold text-sm text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                        <i class='bx bx-mail-send mr-2'></i> Email Templates
                    </button>
                    <button class="w-full text-left px-4 py-3 rounded-xl font-semibold text-sm text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                        <i class='bx bx-receipt mr-2'></i> Invoicing Setup
                    </button>
                </div>

                <!-- Settings Form -->
                <div class="md:col-span-2 premium-card p-6 md:p-8 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
                    <h3 class="text-lg font-bold text-gray-900 border-b border-gray-100 dark:border-gray-800 pb-4 mb-6"><i class='bx bxs-business text-brand-500 mr-2'></i>Agency Profile</h3>
                    
                    <form @submit.prevent="saveSettings" class="space-y-6">
                        <div class="grid grid-cols-2 gap-6">
                            <div class="col-span-2 sm:col-span-1">
                                <label class="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Agency Name</label>
                                <input type="text" v-model="settings.agencyName" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 outline-none transition-all">
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <label class="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Support Email</label>
                                <input type="email" v-model="settings.supportEmail" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 outline-none transition-all">
                            </div>
                            <div class="col-span-2">
                                <label class="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Office Address</label>
                                <textarea v-model="settings.address" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm h-20 resize-none focus:ring-2 focus:ring-brand-500/20 outline-none transition-all"></textarea>
                            </div>
                        </div>

                        <h3 class="text-lg font-bold text-gray-900 border-b border-gray-100 dark:border-gray-800 pb-4 mb-6 mt-8"><i class='bx bx-money text-brand-500 mr-2'></i>Financial Defaults</h3>
                        
                        <div class="grid grid-cols-2 gap-6">
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Primary Currency</label>
                                <select v-model="settings.currency" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 outline-none transition-all appearance-none cursor-pointer">
                                    <option value="INR">₹ INR (Indian Rupee)</option>
                                    <option value="USD">$ USD (US Dollar)</option>
                                    <option value="EUR">€ EUR (Euro)</option>
                                    <option value="GBP">£ GBP (Pound)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Default Tax Rate (%)</label>
                                <input type="number" step="0.01" v-model="settings.taxRate" class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 outline-none transition-all">
                            </div>
                        </div>

                        <div class="pt-6 mt-6 border-t border-gray-100 dark:border-gray-800 flex justify-end">
                            <button type="submit" class="bg-brand-600 hover:bg-brand-700 text-white px-6 py-2.5 rounded-xl text-sm font-bold transition-all shadow-md active:scale-95 flex items-center gap-2">
                                <i v-if="saving" class='bx bx-loader-alt bx-spin text-lg'></i>
                                <i v-else class='bx bx-save text-lg'></i>
                                Save Configuration
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `,
    setup() {
        const saving = ref(false);
        const settings = reactive({
            agencyName: 'TravelAdmin Enterprise',
            supportEmail: 'admin@traveladmin.com',
            address: '123 Tech Park, Innovation Valley',
            currency: 'INR',
            taxRate: 18.0
        });

        const loadSettings = () => {
            const saved = localStorage.getItem('appSettings');
            if (saved) {
                Object.assign(settings, JSON.parse(saved));
            }
        };

        const saveSettings = async () => {
            saving.value = true;
            // Fake API delay
            await new Promise(r => setTimeout(r, 600));
            localStorage.setItem('appSettings', JSON.stringify(settings));
            saving.value = false;
            appState.showToast('Global settings updated successfully', 'success');
        };

        onMounted(() => {
            loadSettings();
        });

        return { settings, saving, saveSettings };
    }
});
