const EmployeeDetailView = defineComponent({
    template: `
        <div>
            <!-- Header -->
            <div class="mb-6 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="$router.push('/employees')" class="p-2 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors">
                        <i class='bx bx-arrow-back text-xl'></i>
                    </button>
                    <h2 class="text-2xl font-bold text-gray-800">Employee Details</h2>
                </div>
                <div v-if="employee && !isEditing" class="flex items-center gap-2">
                    <button @click="openEdit" class="px-3 py-1.5 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-1 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50">
                        <i class='bx bx-edit text-lg'></i> Edit
                    </button>
                    <button @click="deleteEmployee" class="px-3 py-1.5 text-sm font-medium text-red-600 bg-white border border-red-200 rounded-lg hover:bg-red-50 flex items-center gap-1 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500/50">
                        <i class='bx bx-trash text-lg'></i> Delete
                    </button>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="flex flex-col justify-center items-center h-64 text-brand-600">
                <i class='bx bx-loader-alt bx-spin text-4xl mb-2'></i>
                <span class="text-sm font-medium">Loading Employee Data...</span>
            </div>

            <div v-else-if="employee" class="space-y-6">
                <!-- Info Card -->
                <div class="premium-card rounded-2xl p-8 relative animate-fade-in overflow-hidden">
                    <div class="absolute right-0 top-0 w-32 h-32 bg-brand-50 rounded-bl-full opacity-30 -mr-16 -mt-16 group-hover:scale-110 transition-transform"></div>
                    <div v-if="!isEditing" class="flex flex-col md:flex-row gap-8 relative z-10">
                        <div class="flex-1 flex flex-col md:flex-row gap-8 items-center md:items-start text-center md:text-left">
                            <div class="w-24 h-24 rounded-2xl bg-gradient-to-tr from-brand-500 to-brand-400 flex items-center justify-center text-white text-4xl font-black shadow-lg shadow-brand-500/30">
                                {{ employee.employee_name ? employee.employee_name.charAt(0).toUpperCase() : 'E' }}
                            </div>
                            <div class="flex-1">
                                <h3 class="text-3xl font-black text-gray-900 tracking-tight mb-1">{{ employee.employee_name }}</h3>
                                <div class="flex flex-wrap justify-center md:justify-start items-center gap-2 text-sm font-semibold mb-6">
                                    <span class="text-brand-600 bg-brand-50 px-3 py-1 rounded-xl">{{ employee.designation || 'Specialist' }}</span>
                                    <span class="text-gray-300">@</span>
                                    <span class="text-gray-500 hover:text-brand-600 transition-colors cursor-pointer">{{ employee.company_name || 'Individual Contractor' }}</span>
                                </div>
                                
                                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-6 border-t border-gray-100">
                                    <div class="flex flex-col">
                                        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Communication</span>
                                        <div class="text-sm font-bold text-gray-800">{{ employee.phone || 'No Mobile' }}</div>
                                        <div class="text-xs text-gray-400 truncate">{{ employee.email || 'No Email Registered' }}</div>
                                    </div>
                                    <div class="flex flex-col">
                                        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Identity Access</span>
                                        <div class="text-sm font-bold text-gray-800">{{ employee.id_type || 'Unverified' }}</div>
                                        <div class="text-xs text-gray-400">{{ employee.id_number || 'N/A' }}</div>
                                    </div>
                                    <div class="flex flex-col">
                                        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Member Since</span>
                                        <div class="text-sm font-bold text-gray-800">{{ new Date(employee.created_at || Date.now()).toLocaleDateString() }}</div>
                                    </div>
                                    <div class="flex flex-col">
                                        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Capital Output</span>
                                        <div class="text-sm font-bold text-brand-600 flex items-baseline gap-1">
                                            <span class="text-xs">₹</span>{{ employee.bookings.reduce((sum, b) => sum + b.cost, 0).toLocaleString() }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Edit Form -->
                    <form v-else @submit.prevent="saveEmployee" class="space-y-4">
                        <div class="flex justify-between items-center mb-4 pb-2 border-b border-gray-100">
                            <h3 class="text-lg font-bold text-brand-600 flex items-center gap-2"><i class='bx bx-edit'></i> Edit Employee Details</h3>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Full Name *</label>
                                <input type="text" v-model="formData.name" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Phone *</label>
                                <input type="tel" v-model="formData.phone" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Email</label>
                                <input type="email" v-model="formData.email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Designation</label>
                                <input type="text" v-model="formData.designation" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Company</label>
                            <select v-model="formData.company_id" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                                <option :value="null">-- No Company (Individual) --</option>
                                <option v-for="c in companiesOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                            </select>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">ID Type</label>
                                <select v-model="formData.id_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                                    <option value="">-- Select --</option>
                                    <option value="Aadhaar">Aadhaar</option>
                                    <option value="PAN">PAN</option>
                                    <option value="Passport">Passport</option>
                                    <option value="Voter ID">Voter ID</option>
                                    <option value="DL">DL</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">ID Number</label>
                                <input type="text" v-model="formData.id_number" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                        </div>
                        <div class="flex justify-end gap-3 pt-4 border-t border-gray-100">
                            <button type="button" @click="isEditing = false" class="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
                            <button type="submit" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 flex items-center gap-2">
                                <i v-if="saving" class='bx bx-loader-alt bx-spin'></i> Save Changes
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Tabs -->
                <div class="flex gap-4 border-b border-gray-100 dark:border-gray-800">
                    <button @click="activeTab = 'bookings'" :class="['pb-3 text-sm font-bold border-b-2 transition-colors', activeTab === 'bookings' ? 'border-brand-500 text-brand-600' : 'border-transparent text-gray-500 hover:text-gray-800']">
                        <i class='bx bx-book-bookmark'></i> Booking History
                    </button>
                    <button @click="activeTab = 'analytics'" :class="['pb-3 text-sm font-bold border-b-2 transition-colors', activeTab === 'analytics' ? 'border-brand-500 text-brand-600' : 'border-transparent text-gray-500 hover:text-gray-800']">
                        <i class='bx bx-chart'></i> Personal Analytics
                    </button>
                </div>

                <!-- Bookings Tab -->
                <div v-show="activeTab === 'bookings'" class="space-y-4">
                    <!-- Filters -->
                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4 flex md:items-center flex-col md:flex-row justify-between">
                    <div class="font-semibold text-gray-700 flex items-center gap-2">
                        <i class='bx bx-filter-alt'></i> Filter Employee Bookings
                    </div>
                    <div class="flex items-center gap-2">
                        <input type="date" v-model="filters.date_from" @change="fetchData" class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 bg-white text-sm text-gray-700 hover:border-brand-300 transition-colors">
                        <span class="text-gray-400 text-sm">to</span>
                        <input type="date" v-model="filters.date_to" @change="fetchData" class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 bg-white text-sm text-gray-700 hover:border-brand-300 transition-colors">
                    </div>
                </div>

                <!-- Bookings Table -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                        <h4 class="font-semibold text-gray-800">Recent Bookings</h4>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left bg-white text-sm whitespace-nowrap">
                            <thead class="bg-gray-50/50 text-gray-500">
                                <tr>
                                    <th class="px-6 py-4 font-medium">Type</th>
                                    <th class="px-6 py-4 font-medium">Date</th>
                                    <th class="px-6 py-4 font-medium">Route/Item</th>
                                    <th class="px-6 py-4 text-center font-medium">Status</th>
                                    <th class="px-6 py-4 font-medium text-right">Cost</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <tr v-for="b in employee.bookings" :key="b.booking_id" @click="$router.push('/bookings/' + b.booking_id)" class="hover:bg-gray-50/50 transition-colors cursor-pointer group">
                                    <td class="px-6 py-4 font-medium text-gray-800">
                                        <div class="flex items-center gap-2">
                                            <i class='bx' 
                                               :class="{
                                                   'bx-planet text-brand-500': b.booking_type === 'Flight',
                                                   'bx-train text-emerald-500': b.booking_type === 'Train',
                                                   'bx-bus text-orange-500': b.booking_type === 'Bus',
                                                   'bx-building-house text-purple-500': b.booking_type === 'Hotel'
                                               }"></i>
                                            {{ b.booking_type }}
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <div class="text-gray-900">{{ new Date(b.booking_date).toLocaleDateString() }}</div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <div class="text-xs text-gray-700 font-medium">
                                            <span v-if="b.booking_type === 'Hotel'">{{ b.hotel_name }} - {{ b.from_city }}</span>
                                            <span v-else>{{ b.from_city }} <i class='bx bx-right-arrow-alt text-gray-400'></i> {{ b.to_city }}</span>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 text-center">
                                        <span :class="{'bg-green-50 text-green-700': b.status === 'Confirmed', 'bg-yellow-50 text-yellow-700': b.status === 'Pending', 'bg-red-50 text-red-700': b.status === 'Cancelled'}" class="px-2 py-1 rounded-full text-xs font-semibold">{{ b.status }}</span>
                                    </td>
                                    <td class="px-6 py-4 font-medium text-gray-800 text-right">₹{{ b.cost.toLocaleString() }}</td>
                                </tr>
                                <tr v-if="employee.bookings.length === 0">
                                    <td colspan="5" class="px-6 py-8 text-center text-gray-500">
                                        <div class="flex flex-col items-center">
                                            <i class='bx bx-folder-open text-4xl text-gray-300 mb-2'></i>
                                            <p>No bookings found for this employee.</p>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                </div>

                <!-- Analytics Tab -->
                <div v-if="activeTab === 'analytics'" class="space-y-6 animate-fade-in">
                    <!-- Top Level Stats Summary -->
                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-2xl p-5">
                            <div class="text-blue-500 text-3xl mb-2"><i class='bx bxs-plane-alt'></i></div>
                            <div class="text-blue-600 text-[10px] font-black uppercase tracking-widest">Flights</div>
                            <div class="text-2xl font-black text-gray-900 mt-1">{{ analyticsData.types.Flight || 0 }}</div>
                        </div>
                        <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 rounded-2xl p-5">
                            <div class="text-emerald-500 text-3xl mb-2"><i class='bx bxs-train'></i></div>
                            <div class="text-emerald-600 text-[10px] font-black uppercase tracking-widest">Trains</div>
                            <div class="text-2xl font-black text-gray-900 mt-1">{{ analyticsData.types.Train || 0 }}</div>
                        </div>
                        <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-100 dark:border-orange-800 rounded-2xl p-5">
                            <div class="text-orange-500 text-3xl mb-2"><i class='bx bxs-bus'></i></div>
                            <div class="text-orange-600 text-[10px] font-black uppercase tracking-widest">Buses</div>
                            <div class="text-2xl font-black text-gray-900 mt-1">{{ analyticsData.types.Bus || 0 }}</div>
                        </div>
                        <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800 rounded-2xl p-5">
                            <div class="text-purple-500 text-3xl mb-2"><i class='bx bxs-building-house'></i></div>
                            <div class="text-purple-600 text-[10px] font-black uppercase tracking-widest">Hotels</div>
                            <div class="text-2xl font-black text-gray-900 mt-1">{{ analyticsData.types.Hotel || 0 }}</div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Cost Distribution -->
                        <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
                            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6">Spend by Categorical Service</h4>
                            <div class="space-y-4">
                                <div v-for="(amount, type) in analyticsData.costByType" :key="type">
                                    <div class="flex justify-between text-sm mb-1">
                                        <span class="font-bold text-gray-700 dark:text-gray-200">{{ type }}</span>
                                        <span class="font-bold text-gray-900 dark:text-gray-100">₹{{ amount.toLocaleString() }}</span>
                                    </div>
                                    <div class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5">
                                        <div :class="['h-2.5 rounded-full', 
                                            type === 'Flight' ? 'bg-blue-500' : 
                                            (type === 'Train' ? 'bg-emerald-500' : 
                                            (type === 'Bus' ? 'bg-orange-500' : 'bg-purple-500'))
                                        ]" :style="'width: ' + ((amount / (employee.bookings.reduce((sum, b) => sum + b.cost, 0) || 1)) * 100) + '%'"></div>
                                    </div>
                                </div>
                                <div v-if="Object.keys(analyticsData.costByType).length === 0" class="text-sm text-gray-400 text-center py-4">No spend data available.</div>
                            </div>
                        </div>
                        <!-- Status Breakdown -->
                        <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
                            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6">Trip Status Overview</h4>
                            <div class="space-y-4 flex flex-col justify-center h-full">
                                <div class="flex items-center gap-4">
                                    <div class="w-3 h-3 rounded-full bg-green-500 shrink-0"></div>
                                    <div class="flex-1 text-sm font-bold text-gray-700 dark:text-gray-200">Confirmed</div>
                                    <div class="font-black">{{ analyticsData.statuses.Confirmed || 0 }}</div>
                                </div>
                                <div class="flex items-center gap-4">
                                    <div class="w-3 h-3 rounded-full bg-yellow-500 shrink-0"></div>
                                    <div class="flex-1 text-sm font-bold text-gray-700 dark:text-gray-200">Pending</div>
                                    <div class="font-black">{{ analyticsData.statuses.Pending || 0 }}</div>
                                </div>
                                <div class="flex items-center gap-4">
                                    <div class="w-3 h-3 rounded-full bg-gray-500 shrink-0"></div>
                                    <div class="flex-1 text-sm font-bold text-gray-700 dark:text-gray-200">Completed</div>
                                    <div class="font-black">{{ analyticsData.statuses.Completed || 0 }}</div>
                                </div>
                                <div class="flex items-center gap-4">
                                    <div class="w-3 h-3 rounded-full bg-red-500 shrink-0"></div>
                                    <div class="flex-1 text-sm font-bold text-gray-700 dark:text-gray-200">Cancelled</div>
                                    <div class="font-black">{{ analyticsData.statuses.Cancelled || 0 }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
            
            <div v-else class="flex justify-center items-center h-64 text-red-500">
                <i class='bx bx-error-circle text-4xl mb-2'></i>
                <span class="text-sm font-medium">Failed to load employee details.</span>
            </div>
        </div>
    `,
    setup() {
        const route = VueRouter.useRoute();
        const router = VueRouter.useRouter();
        const employee = ref(null);
        const loading = ref(true);
        const companiesOptions = ref([]);
        const isEditing = ref(false);
        const saving = ref(false);
        const activeTab = ref('bookings');
        const formData = reactive({
            name: '', phone: '', email: '', designation: '', company_id: null, id_type: '', id_number: ''
        });
        const filters = reactive({ date_from: '', date_to: '' });

        const analyticsData = computed(() => {
            if (!employee.value || !employee.value.bookings) return { types: {}, costByType: {}, statuses: {} };
            const types = {};
            const costByType = {};
            const statuses = {};

            employee.value.bookings.forEach(b => {
                types[b.booking_type] = (types[b.booking_type] || 0) + 1;
                costByType[b.booking_type] = (costByType[b.booking_type] || 0) + b.cost;
                statuses[b.status] = (statuses[b.status] || 0) + 1;
            });

            return { types, costByType, statuses };
        });

        const fetchData = async () => {
            loading.value = true;
            try {
                let url = `/api/employees/${route.params.id}/bookings?`;
                if (filters.date_from) url += `date_from=${filters.date_from}&`;
                if (filters.date_to) url += `date_to=${filters.date_to}&`;

                employee.value = await api.request(url);
            } catch (error) {
                console.error(error);
                appState.showToast('Failed to load employee detail data', 'error');
            } finally {
                loading.value = false;
            }
        };

        const fetchCompanies = async () => {
            try {
                const res = await api.request('/api/companies?size=200');
                companiesOptions.value = res.items || [];
            } catch (error) { }
        };

        const openEdit = () => {
            Object.assign(formData, {
                // The endpoint returns employee_name etc. mixed with employee.
                // We will populate with what we have from the employee summary/bookings endpoint.
                name: employee.value.employee_name || '',
                phone: employee.value.phone || '',
                email: employee.value.email || '',
                designation: employee.value.designation || '',
                company_id: employee.value.company_id || null,
                id_type: employee.value.id_type || '',
                id_number: employee.value.id_number || ''
            });
            isEditing.value = true;
        };

        const saveEmployee = async () => {
            if (!formData.name || !formData.phone) return appState.showToast('Name and Phone are required', 'error');
            saving.value = true;
            try {
                await api.request(`/api/employees/${employee.value.employee_id || route.params.id}`, { method: 'PUT', body: formData });
                appState.showToast('Employee updated successfully');
                isEditing.value = false;
                fetchData();
            } catch (error) {
            } finally {
                saving.value = false;
            }
        };

        const deleteEmployee = async () => {
            if (confirm('Are you sure you want to delete this employee? Linked bookings might be affected.')) {
                try {
                    await api.request(`/api/employees/${employee.value.employee_id || route.params.id}`, { method: 'DELETE' });
                    appState.showToast('Employee deleted successfully');
                    router.push('/employees');
                } catch (e) {
                }
            }
        };

        onMounted(() => {
            fetchData();
            fetchCompanies();
        });

        watch(
            () => route.params.id,
            () => {
                if (route.name === 'employeeDetail') fetchData();
            }
        );

        return {
            employee, loading, filters, fetchData, isEditing, saving, formData, openEdit, saveEmployee, deleteEmployee, companiesOptions,
            activeTab, analyticsData
        };
    }
});
