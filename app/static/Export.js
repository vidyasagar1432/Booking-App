const ExportView = defineComponent({
    template: `
        <div class="space-y-6 max-w-4xl mx-auto">
            <div class="premium-card p-8 rounded-3xl animate-fade-in relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-brand-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
                <div class="absolute bottom-0 left-0 w-48 h-48 bg-accent-500/5 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none"></div>

                <div class="relative z-10 flex flex-col items-center text-center mb-8 pb-8 border-b border-gray-100 dark:border-gray-700">
                    <div class="w-16 h-16 bg-brand-50 rounded-2xl flex items-center justify-center text-brand-600 mb-4 shadow-sm">
                        <i class='bx bx-cloud-download text-3xl'></i>
                    </div>
                    <h2 class="text-2xl font-bold text-gray-900 leading-tight">Export Data</h2>
                    <p class="text-sm text-gray-500 mt-2 max-w-md">Customize what information you want to pull into your Excel spreadsheet. Select the entities and refine the dataset using the filters below.</p>
                </div>

                <div class="relative z-10 space-y-8">
                    <!-- Entities Section -->
                    <div class="space-y-4">
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest px-2">1. Select Entities to Export</label>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 px-2">
                            <!-- Bookings -->
                            <div @click="filters.entity_bookings = !filters.entity_bookings" 
                                 :class="['p-4 rounded-2xl border-2 transition-all cursor-pointer flex items-center justify-between group', 
                                         filters.entity_bookings ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/10' : 'border-gray-100 hover:border-brand-200 dark:border-gray-700']">
                                <div class="flex items-center gap-3">
                                    <div :class="['w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-colors', filters.entity_bookings ? 'bg-brand-100 text-brand-600 dark:bg-brand-800 dark:text-brand-300' : 'bg-gray-50 text-gray-400 group-hover:text-brand-500 dark:bg-gray-800']">
                                        <i class='bx bx-book-content'></i>
                                    </div>
                                    <div class="text-sm font-bold text-gray-800">Bookings</div>
                                </div>
                                <div :class="['w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors', filters.entity_bookings ? 'bg-brand-500 border-brand-500' : 'border-gray-300']">
                                    <i v-if="filters.entity_bookings" class='bx bx-check text-white text-sm'></i>
                                </div>
                            </div>
                            <!-- Employees -->
                            <div @click="filters.entity_employees = !filters.entity_employees" 
                                 :class="['p-4 rounded-2xl border-2 transition-all cursor-pointer flex items-center justify-between group', 
                                         filters.entity_employees ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/10' : 'border-gray-100 hover:border-brand-200 dark:border-gray-700']">
                                <div class="flex items-center gap-3">
                                    <div :class="['w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-colors', filters.entity_employees ? 'bg-brand-100 text-brand-600 dark:bg-brand-800 dark:text-brand-300' : 'bg-gray-50 text-gray-400 group-hover:text-brand-500 dark:bg-gray-800']">
                                        <i class='bx bx-user-circle'></i>
                                    </div>
                                    <div class="text-sm font-bold text-gray-800">Employees</div>
                                </div>
                                <div :class="['w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors', filters.entity_employees ? 'bg-brand-500 border-brand-500' : 'border-gray-300']">
                                    <i v-if="filters.entity_employees" class='bx bx-check text-white text-sm'></i>
                                </div>
                            </div>
                            <!-- Companies -->
                            <div @click="filters.entity_companies = !filters.entity_companies" 
                                 :class="['p-4 rounded-2xl border-2 transition-all cursor-pointer flex items-center justify-between group', 
                                         filters.entity_companies ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/10' : 'border-gray-100 hover:border-brand-200 dark:border-gray-700']">
                                <div class="flex items-center gap-3">
                                    <div :class="['w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-colors', filters.entity_companies ? 'bg-brand-100 text-brand-600 dark:bg-brand-800 dark:text-brand-300' : 'bg-gray-50 text-gray-400 group-hover:text-brand-500 dark:bg-gray-800']">
                                        <i class='bx bx-buildings'></i>
                                    </div>
                                    <div class="text-sm font-bold text-gray-800">Companies</div>
                                </div>
                                <div :class="['w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors', filters.entity_companies ? 'bg-brand-500 border-brand-500' : 'border-gray-300']">
                                    <i v-if="filters.entity_companies" class='bx bx-check text-white text-sm'></i>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="filters.entity_bookings" class="px-2 pt-4 border-t border-gray-100 dark:border-gray-700 animate-in slide-in-from-bottom-2 fade-in">
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">2. Refine Bookings Data</label>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div>
                                <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">Date From</label>
                                <input type="date" v-model="filters.date_from" class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-sm font-medium focus:ring-2 focus:ring-brand-500/20 outline-none text-gray-700">
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">Date To</label>
                                <input type="date" v-model="filters.date_to" class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-sm font-medium focus:ring-2 focus:ring-brand-500/20 outline-none text-gray-700">
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">Service Type</label>
                                <select v-model="filters.booking_type" class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-sm font-medium outline-none focus:ring-2 focus:ring-brand-500/20 text-gray-700">
                                    <option value="">All Types</option>
                                    <option value="Flight">Flight</option>
                                    <option value="Train">Train</option>
                                    <option value="Bus">Bus</option>
                                    <option value="Hotel">Hotel</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">Status</label>
                                <select v-model="filters.booking_status" class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-sm font-medium outline-none focus:ring-2 focus:ring-brand-500/20 text-gray-700">
                                    <option value="">All Statuses</option>
                                    <option value="Confirmed">Confirmed</option>
                                    <option value="Completed">Completed</option>
                                    <option value="Pending">Pending</option>
                                    <option value="Cancelled">Cancelled</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="px-2 pt-6 pb-2 text-center">
                        <button @click="triggerExport" :disabled="isExporting" 
                                class="w-full sm:w-auto min-w-[200px] bg-gray-900 dark:bg-white dark:text-gray-900 text-white hover:bg-black dark:hover:bg-gray-100 px-6 py-3.5 rounded-xl font-bold transition-all shadow-lg active:scale-95 flex items-center justify-center gap-2 mx-auto disabled:opacity-50">
                            <i v-if="isExporting" class='bx bx-loader-alt bx-spin text-xl'></i>
                            <i v-else class='bx bx-download text-xl'></i>
                            {{ isExporting ? 'Generating Excel...' : 'Generate Spreadsheet' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `,
    setup() {
        const filters = reactive({
            entity_bookings: true,
            entity_employees: true,
            entity_companies: true,
            date_from: '',
            date_to: '',
            booking_type: '',
            booking_status: ''
        });

        const isExporting = ref(false);

        const triggerExport = async () => {
            if (!filters.entity_bookings && !filters.entity_employees && !filters.entity_companies) {
                return appState.showToast('Please select at least one entity to export', 'error');
            }

            isExporting.value = true;
            try {
                // Build query params
                const params = new URLSearchParams();
                params.append('entity_bookings', filters.entity_bookings);
                params.append('entity_employees', filters.entity_employees);
                params.append('entity_companies', filters.entity_companies);

                if (filters.entity_bookings) {
                    if (filters.date_from) params.append('date_from', filters.date_from);
                    if (filters.date_to) params.append('date_to', filters.date_to);
                    if (filters.booking_type) params.append('booking_type', filters.booking_type);
                    if (filters.booking_status) params.append('booking_status', filters.booking_status);
                }

                const blob = await api.request(`/api/admin/export?${params.toString()}`, { responseType: 'blob' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `TravelAdmin_Export_${new Date().toISOString().split('T')[0]}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                appState.showToast('Excel file generated successfully!', 'success');
            } catch (e) {
                console.error(e);
                appState.showToast('Failed to export. Check server logs.', 'error');
            } finally {
                isExporting.value = false;
            }
        };

        return { filters, isExporting, triggerExport };
    }
});
