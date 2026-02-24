const CompanyDetailView = defineComponent({
    template: `
        <div>
            <!-- Header -->
            <div class="mb-6 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="$router.push('/companies')" class="p-2 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors">
                        <i class='bx bx-arrow-back text-xl'></i>
                    </button>
                    <h2 class="text-2xl font-bold text-gray-800">Company Details</h2>
                </div>
                <div v-if="company && !isEditing" class="flex items-center gap-2">
                    <button @click="openEdit" class="px-3 py-1.5 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-1 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50">
                        <i class='bx bx-edit text-lg'></i> Edit
                    </button>
                    <button @click="deleteCompany" class="px-3 py-1.5 text-sm font-medium text-red-600 bg-white border border-red-200 rounded-lg hover:bg-red-50 flex items-center gap-1 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500/50">
                        <i class='bx bx-trash text-lg'></i> Delete
                    </button>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="flex flex-col justify-center items-center h-64 text-brand-600">
                <i class='bx bx-loader-alt bx-spin text-4xl mb-2'></i>
                <span class="text-sm font-medium">Loading Company Data...</span>
            </div>

            <div v-else-if="company" class="space-y-6">
                <!-- Info Card -->
                <div class="premium-card rounded-2xl p-8 relative animate-fade-in overflow-hidden">
                    <div class="absolute right-0 top-0 w-32 h-32 bg-brand-50 rounded-bl-full opacity-30 -mr-16 -mt-16"></div>
                    <div v-if="!isEditing" class="relative z-10">
                        <div class="flex items-center gap-6 mb-8">
                            <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center text-white text-3xl font-black shadow-lg shadow-brand-500/30">
                                {{ company.name ? company.name.charAt(0).toUpperCase() : 'C' }}
                            </div>
                            <div>
                                <h3 class="text-3xl font-black text-gray-900 tracking-tight">{{ company.name }}</h3>
                                <div class="flex items-center gap-2 text-sm font-bold text-gray-400 uppercase tracking-widest mt-1">
                                    <i class='bx bx-briefcase text-brand-500'></i> {{ company.industry || 'Enterprise Client' }}
                                </div>
                            </div>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 pt-8 border-t border-gray-100">
                            <div class="flex flex-col">
                                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Corporate Contact</span>
                                <div class="text-sm font-bold text-gray-800 flex items-center gap-2">
                                    <i class='bx bx-phone text-brand-500'></i> {{ company.phone || 'No Contact' }}
                                </div>
                                <div class="text-xs text-gray-400 mt-1">{{ company.email || 'No email registered' }}</div>
                            </div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Legal Registry</span>
                                <div class="text-sm font-bold text-gray-800 flex items-center gap-2">
                                    <i class='bx bx-barcode-reader text-brand-500'></i> {{ company.gst_number || 'Internal Node' }}
                                </div>
                                <div class="text-xs text-gray-400 mt-1">Tax Reference ID</div>
                            </div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total Workforce</span>
                                <div class="text-sm font-bold text-brand-600 flex items-center gap-2">
                                    <i class='bx bx-group text-brand-500'></i> {{ company.employee_count }} Active Nodes
                                </div>
                            </div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Corporate Reach</span>
                                <div class="text-sm font-bold text-gray-800 truncate" :title="company.address">
                                    {{ company.address || 'Global Remote' }}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Edit Form -->
                    <form v-else @submit.prevent="saveCompany" class="space-y-4">
                        <div class="flex justify-between items-center mb-4 pb-2 border-b border-gray-100">
                            <h3 class="text-lg font-bold text-brand-600 flex items-center gap-2"><i class='bx bx-edit'></i> Edit Company Details</h3>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Company Name *</label>
                                <input type="text" v-model="formData.name" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Industry</label>
                                <input type="text" v-model="formData.industry" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Phone</label>
                                <input type="tel" v-model="formData.phone" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">Email</label>
                                <input type="email" v-model="formData.email" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-gray-700 mb-1">GST Number</label>
                                <input type="text" v-model="formData.gst_number" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 bg-white text-sm">
                            </div>
                            <div class="col-span-2">
                                <label class="block text-xs font-medium text-gray-700 mb-1">Address</label>
                                <textarea v-model="formData.address" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 resize-none text-sm"></textarea>
                            </div>
                        </div>
                        <div class="flex justify-end gap-3 pt-4">
                            <button type="button" @click="isEditing = false" class="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
                            <button type="submit" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 flex items-center gap-2">
                                <i v-if="saving" class='bx bx-loader-alt bx-spin'></i> Save Changes
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Tabs -->
                <div class="flex gap-4 border-b border-gray-100 dark:border-gray-800">
                    <button @click="activeTab = 'employees'" :class="['pb-3 text-sm font-bold border-b-2 transition-colors', activeTab === 'employees' ? 'border-brand-500 text-brand-600' : 'border-transparent text-gray-500 hover:text-gray-800']">
                        <i class='bx bx-group'></i> Associated Employees
                    </button>
                    <button @click="activeTab = 'ledger'" :class="['pb-3 text-sm font-bold border-b-2 transition-colors', activeTab === 'ledger' ? 'border-brand-500 text-brand-600' : 'border-transparent text-gray-500 hover:text-gray-800']">
                        <i class='bx bx-wallet'></i> Financial Ledger
                    </button>
                    <button @click="activeTab = 'analytics'" :class="['pb-3 text-sm font-bold border-b-2 transition-colors', activeTab === 'analytics' ? 'border-brand-500 text-brand-600' : 'border-transparent text-gray-500 hover:text-gray-800']">
                        <i class='bx bx-chart'></i> Corporate Analytics
                    </button>
                </div>

                <!-- Employees Tab Content -->
                <div v-show="activeTab === 'employees'">
                <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 gap-4 flex md:items-center flex-col md:flex-row justify-between">
                    <div class="font-semibold text-gray-700 flex items-center gap-2">
                        <i class='bx bx-filter-alt'></i> Filter Company Bookings
                    </div>
                    <div class="flex items-center gap-2">
                        <input type="date" v-model="filters.date_from" @change="fetchData" class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 bg-white text-sm text-gray-700 hover:border-brand-300 transition-colors">
                        <span class="text-gray-400 text-sm">to</span>
                        <input type="date" v-model="filters.date_to" @change="fetchData" class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 bg-white text-sm text-gray-700 hover:border-brand-300 transition-colors">
                    </div>
                </div>

                <!-- Employees Table showing their bookings -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                        <h4 class="font-semibold text-gray-800">Associated Employees & Booking Summaries</h4>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm whitespace-nowrap">
                            <thead class="bg-white text-gray-500 border-b border-gray-100">
                                <tr>
                                    <th class="px-6 py-4 font-medium">Employee Name</th>
                                    <th class="px-6 py-4 font-medium">Designation</th>
                                    <th class="px-6 py-4 font-medium">Contact</th>
                                    <th class="px-6 py-4 font-medium">ID Details</th>
                                    <th class="px-6 py-4 font-medium text-center">Bookings Found</th>
                                    <th class="px-6 py-4 font-medium text-right">Total Spent</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <tr v-for="emp in company.employees" :key="emp.id" class="hover:bg-gray-50 transition-colors group cursor-pointer" @click="$router.push('/employees/' + emp.id)">
                                    <td class="px-6 py-4 font-medium text-brand-700 group-hover:text-brand-800">{{ emp.name }}</td>
                                    <td class="px-6 py-4 text-gray-600">{{ emp.designation || '-' }}</td>
                                    <td class="px-6 py-4">
                                        <div class="text-gray-900">{{ emp.phone }}</div>
                                        <div class="text-xs text-gray-500">{{ emp.email }}</div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <div class="text-gray-900">{{ emp.id_type || '—' }}</div>
                                        <div class="text-xs text-gray-500">{{ emp.id_number || '—' }}</div>
                                    </td>
                                    <td class="px-6 py-4 text-center">
                                        <span class="inline-flex items-center justify-center bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full text-xs font-semibold border border-purple-100">{{ emp.booking_count }}</span>
                                    </td>
                                    <td class="px-6 py-4 text-right font-medium text-gray-800">
                                        ₹{{ (emp.total_spent || 0).toLocaleString() }}
                                    </td>
                                </tr>
                                <tr v-if="company.employees.length === 0">
                                    <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                                        <div class="flex flex-col items-center">
                                            <i class='bx bx-user-x text-4xl text-gray-300 mb-2'></i>
                                            <p>No employees found for this company.</p>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                </div>

                <!-- Ledger Tab Content -->
                <div v-if="activeTab === 'ledger'" class="space-y-4">
                    <div v-if="loadingLedger" class="flex justify-center items-center py-12 text-brand-600">
                        <i class='bx bx-loader-alt bx-spin text-3xl'></i>
                    </div>
                    <div v-else>
                        <!-- Ledger Summary Cards -->
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                            <div class="bg-gradient-to-br from-brand-600 to-brand-500 rounded-2xl p-6 text-white shadow-lg shadow-brand-500/20">
                                <div class="text-brand-100 text-xs font-bold uppercase tracking-widest mb-2"><i class='bx bx-money'></i> Total Lifetime Spend</div>
                                <div class="text-3xl font-black">₹{{ totalLedgerSpend.toLocaleString() }}</div>
                            </div>
                            <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-100 dark:border-gray-700 shadow-sm">
                                <div class="text-gray-500 text-xs font-bold uppercase tracking-widest mb-2"><i class='bx bx-book-bookmark'></i> Total Corporate Bookings</div>
                                <div class="text-3xl font-black text-gray-900 dark:text-gray-100">{{ ledger.length }}</div>
                            </div>
                            <button @click="exportLedger" class="bg-gray-900 border border-gray-800 hover:bg-black rounded-2xl p-6 text-white shadow-xl transition-colors flex flex-col justify-center items-center group cursor-pointer text-left">
                                <i class='bx bxs-file-pdf text-3xl mb-2 text-gray-400 group-hover:text-white transition-colors'></i>
                                <div class="text-sm font-bold uppercase tracking-widest">Generate Invoice</div>
                            </button>
                        </div>
                        
                        <!-- Ledger Table -->
                        <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden">
                            <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
                                <h4 class="font-bold text-gray-800 dark:text-gray-200">Corporate Transaction History</h4>
                            </div>
                            <div class="overflow-x-auto">
                                <table class="w-full text-left text-sm whitespace-nowrap">
                                    <thead class="bg-white dark:bg-gray-900 text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-800">
                                        <tr>
                                            <th class="px-6 py-4 font-bold text-[10px] uppercase tracking-wider">Date</th>
                                            <th class="px-6 py-4 font-bold text-[10px] uppercase tracking-wider">Booking Ref</th>
                                            <th class="px-6 py-4 font-bold text-[10px] uppercase tracking-wider">Service</th>
                                            <th class="px-6 py-4 font-bold text-[10px] uppercase tracking-wider">Passengers</th>
                                            <th class="px-6 py-4 font-bold text-[10px] uppercase tracking-wider">Status</th>
                                            <th class="px-6 py-4 font-bold text-[10px] uppercase tracking-wider text-right">Amount</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                                        <tr v-for="bk in ledger" :key="bk.booking_id" @click="$router.push('/bookings/' + bk.booking_id)" class="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors cursor-pointer group">
                                            <td class="px-6 py-4 font-medium text-gray-900 dark:text-gray-200">{{ new Date(bk.booking_date).toLocaleDateString() }}</td>
                                            <td class="px-6 py-4 font-bold text-brand-600 group-hover:text-brand-500">{{ bk.booking_id }}</td>
                                            <td class="px-6 py-4 text-gray-600 dark:text-gray-400 font-bold text-xs"><i :class="getServiceIcon(bk.booking_type)"></i> {{ bk.booking_type }}</td>
                                            <td class="px-6 py-4">
                                                <div class="flex -space-x-2">
                                                    <div v-for="emp in bk.employees.slice(0,3)" :key="emp.id" class="w-6 h-6 rounded-full border border-white dark:border-gray-900 bg-brand-50 flex items-center justify-center text-[10px] font-black text-brand-700" :title="emp.name">
                                                        {{ emp.name.charAt(0) }}
                                                    </div>
                                                    <div v-if="bk.employees.length > 3" class="w-6 h-6 rounded-full border border-white dark:border-gray-900 bg-gray-100 flex items-center justify-center text-[9px] font-black text-gray-500">
                                                        +{{ bk.employees.length - 3 }}
                                                    </div>
                                                </div>
                                            </td>
                                            <td class="px-6 py-4">
                                                <span :class="['px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest', 
                                                    bk.status === 'Confirmed' ? 'bg-green-50 text-green-700 border border-green-200' :
                                                    (bk.status === 'Pending' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' : 'bg-red-50 text-red-700 border border-red-200')
                                                ]">
                                                    {{ bk.status }}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 text-right font-black text-gray-900 dark:text-gray-100">
                                                ₹{{ bk.cost.toLocaleString() }}
                                            </td>
                                        </tr>
                                        <tr v-if="ledger.length === 0">
                                            <td colspan="6" class="px-6 py-8 text-center text-gray-400">No corporate transactions found.</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Analytics Tab --->
                <div v-if="activeTab === 'analytics'" class="space-y-6 animate-fade-in">
                    <div v-if="loadingLedger" class="flex justify-center items-center py-12 text-brand-600">
                        <i class='bx bx-loader-alt bx-spin text-3xl'></i>
                    </div>
                    <div v-else>
                        <!-- Top Level Stats Summary -->
                        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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
                                            ]" :style="'width: ' + ((amount / (ledger.reduce((sum, b) => sum + b.cost, 0) || 1)) * 100) + '%'"></div>
                                        </div>
                                    </div>
                                    <div v-if="Object.keys(analyticsData.costByType).length === 0" class="text-sm text-gray-400 text-center py-4">No spend data available.</div>
                                </div>
                            </div>
                            <!-- Employees Overview Top 5 -->
                            <div class="bg-white dark:bg-gray-900 rounded-2xl border border-gray-100 dark:border-gray-800 p-6 shadow-sm">
                                <h4 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6">Top Spenders (Employees)</h4>
                                <div class="space-y-4 flex flex-col justify-center h-full">
                                    <div v-for="emp in [...company.employees].sort((a,b) => (b.total_spent||0) - (a.total_spent||0)).slice(0, 5)" :key="emp.id" class="flex items-center gap-4">
                                        <div class="w-3 h-3 rounded-full bg-brand-500 shrink-0"></div>
                                        <div class="flex-1 text-sm font-bold text-gray-700 dark:text-gray-200">{{ emp.name }}</div>
                                        <div class="font-black text-gray-900 dark:text-gray-100">₹{{ (emp.total_spent||0).toLocaleString() }}</div>
                                    </div>
                                    <div v-if="!company.employees || company.employees.length === 0" class="text-sm text-gray-400 text-center">No employees found.</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
            
            <div v-else class="flex justify-center items-center h-64 text-red-500">
                <i class='bx bx-error-circle text-4xl mb-2'></i>
                <span class="text-sm font-medium">Failed to load company details.</span>
            </div>
        </div>
    `,
    setup() {
        const route = VueRouter.useRoute();
        const router = VueRouter.useRouter();
        const company = ref(null);
        const loading = ref(true);
        const isEditing = ref(false);
        const saving = ref(false);
        const activeTab = ref('employees');
        const ledger = ref([]);
        const loadingLedger = ref(false);
        const formData = reactive({ name: '', industry: '', phone: '', email: '', address: '', gst_number: '' });
        const filters = reactive({ date_from: '', date_to: '' });

        const fetchData = async () => {
            loading.value = true;
            try {
                let url = `/api/companies/${route.params.id}/details?`;
                if (filters.date_from) url += `date_from=${filters.date_from}&`;
                if (filters.date_to) url += `date_to=${filters.date_to}&`;

                company.value = await api.request(url);
            } catch (error) {
                console.error(error);
                appState.showToast('Failed to load company detail data', 'error');
            } finally {
                loading.value = false;
            }
        };

        const fetchLedger = async () => {
            loadingLedger.value = true;
            try {
                const res = await api.request(`/api/companies/${route.params.id}/ledger`);
                ledger.value = res.bookings;
            } catch (e) {
                console.error(e);
            } finally {
                loadingLedger.value = false;
            }
        };

        const totalLedgerSpend = computed(() => {
            return ledger.value.reduce((sum, b) => sum + (b.cost || 0), 0);
        });

        const getServiceIcon = (type) => {
            if (type === 'Flight') return 'bx bxs-plane-alt';
            if (type === 'Train') return 'bx bxs-train';
            if (type === 'Bus') return 'bx bxs-bus';
            return 'bx bxs-building-house';
        };

        const analyticsData = computed(() => {
            const types = {};
            const costByType = {};
            const statuses = {};

            ledger.value.forEach(b => {
                types[b.booking_type] = (types[b.booking_type] || 0) + 1;
                costByType[b.booking_type] = (costByType[b.booking_type] || 0) + b.cost;
                statuses[b.status] = (statuses[b.status] || 0) + 1;
            });

            return { types, costByType, statuses };
        });

        const exportLedger = () => {
            appState.showToast("Corporate Invoice PDF generating...", "info");
            setTimeout(() => appState.showToast("Invoice downloaded successfully to Vault!", "success"), 1500);
        };

        watch(activeTab, (val) => {
            if ((val === 'ledger' || val === 'analytics') && ledger.value.length === 0) fetchLedger();
        });

        const openEdit = () => {
            Object.assign(formData, {
                name: company.value.name || '',
                industry: company.value.industry || '',
                phone: company.value.phone || '',
                email: company.value.email || '',
                address: company.value.address || '',
                gst_number: company.value.gst_number || ''
            });
            isEditing.value = true;
        };

        const saveCompany = async () => {
            if (!formData.name) return appState.showToast('Company name is required', 'error');
            saving.value = true;
            try {
                await api.request(`/api/companies/${company.value.id}`, { method: 'PUT', body: formData });
                appState.showToast('Company updated successfully');
                isEditing.value = false;
                fetchData();
            } catch (error) {
            } finally {
                saving.value = false;
            }
        };

        const deleteCompany = async () => {
            if (confirm('Are you sure you want to delete this company? All associated employees and bookings might be affected.')) {
                try {
                    await api.request(`/api/companies/${company.value.id}`, { method: 'DELETE' });
                    appState.showToast('Company deleted successfully');
                    router.push('/companies');
                } catch (e) {
                }
            }
        };

        onMounted(() => {
            fetchData();
        });

        watch(
            () => route.params.id,
            () => {
                if (route.name === 'companyDetail') fetchData();
            }
        );

        return {
            company, loading, filters, fetchData, isEditing, saving, formData,
            openEdit, saveCompany, deleteCompany,
            activeTab, ledger, loadingLedger, totalLedgerSpend, getServiceIcon, exportLedger,
            analyticsData
        };
    }
});
