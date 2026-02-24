const EmployeesView = defineComponent({
    template: `
        <div class="space-y-6">
            <!-- Header Actions -->
            <div class="premium-card p-4 rounded-2xl flex flex-col lg:flex-row justify-between lg:items-center gap-4">
                <div class="flex flex-wrap items-center gap-4 flex-1">
                    <div class="relative min-w-[260px]">
                        <i class='bx bx-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl'></i>
                        <input type="text" v-model="filters.search" @input="debouncedFetch" placeholder="Search by name, email, phone..." 
                               class="w-full pl-12 pr-4 py-2.5 bg-gray-50 border-none rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:bg-white transition-all font-medium placeholder-gray-400 shadow-sm">
                    </div>
                    
                    <div class="flex items-center gap-2 bg-gray-50 p-1 rounded-xl border border-gray-100/50 flex-wrap">
                        <select v-model="filters.company_id" class="bg-transparent border-none text-xs font-bold uppercase tracking-wider text-gray-500 py-1.5 px-3 focus:ring-0 cursor-pointer hover:bg-white rounded-lg transition-colors min-w-[140px]">
                            <option value="">All Companies</option>
                            <option v-for="c in companiesOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                        </select>
                        <span class="w-px h-4 bg-gray-200 mx-1"></span>
                        <select v-model="filters.sort_by" @change="fetchEmployees" class="bg-transparent border-none text-[10px] font-black uppercase tracking-tighter text-gray-400 py-1.5 px-2 focus:ring-0 cursor-pointer">
                            <option value="created_at">Joined Date</option>
                            <option value="name">Name (A-Z)</option>
                        </select>
                        <button @click="filters.order = filters.order === 'asc' ? 'desc' : 'asc'; fetchEmployees()" 
                                class="w-8 h-8 flex items-center justify-center bg-white rounded-lg text-gray-400 hover:text-brand-600 shadow-sm transition-all active:scale-95">
                            <i :class="['bx text-lg', filters.order === 'asc' ? 'bx-sort-a-z' : 'bx-sort-z-a']"></i>
                        </button>
                    </div>
                </div>
                <button @click="openModal()" class="bg-brand-600 hover:bg-brand-700 text-white pl-4 pr-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-brand-500/20 flex items-center gap-2 shrink-0 active:scale-95">
                    <i class='bx bx-user-plus text-xl'></i> Add Employee
                </button>
            </div>

            <!-- List Table -->
            <div class="premium-card rounded-2xl overflow-hidden animate-fade-in">
                <div v-if="loading" class="flex justify-center items-center h-32 text-brand-600">
                    <i class='bx bx-loader-alt bx-spin text-2xl'></i>
                </div>
                
                <table v-else class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-gray-50/50 border-b border-gray-100 text-xs uppercase tracking-wider text-gray-500 font-semibold">
                            <th class="px-6 py-4">Employee</th>
                            <th class="px-6 py-4">Company</th>
                            <th class="px-6 py-4">Contact</th>
                            <th class="px-6 py-4">ID Details</th>
                            <th class="px-6 py-4 text-center">Bookings</th>
                            <th class="px-6 py-4 text-right">Spent</th>
                            <th class="px-6 py-4 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 text-sm">
                        <tr v-if="!employees || employees.length === 0">
                            <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                                <div class="flex flex-col items-center justify-center">
                                    <i class='bx bx-user-circle text-4xl text-gray-300 mb-2'></i>
                                    <p>No employees found.</p>
                                </div>
                            </td>
                        </tr>
                        <tr v-for="emp in employees" :key="emp.id" @click="$router.push('/employees/' + emp.id)" class="hover:bg-gray-50/50 transition-colors group bg-white cursor-pointer">
                            <td class="px-6 py-4">
                                <div class="font-medium text-gray-900 flex items-center gap-2">
                                    {{ emp.name }}
                                    <span v-if="!emp.is_active" class="px-1.5 py-0.5 rounded bg-gray-100 text-[10px] text-gray-400 uppercase font-bold">Inactive</span>
                                </div>
                                <div class="text-xs text-gray-500 mt-0.5">{{ emp.designation || 'N/A' }}</div>
                            </td>
                            <td class="px-6 py-4">
                                <div class="font-medium text-brand-700">{{ emp.company_name || 'Individual' }}</div>
                            </td>
                            <td class="px-6 py-4">
                                <div class="text-gray-900">{{ emp.phone }}</div>
                                <div class="text-xs text-gray-500">{{ emp.email || '—' }}</div>
                            </td>
                            <td class="px-6 py-4">
                                <div class="text-gray-900">{{ emp.id_type || '—' }}</div>
                                <div class="text-xs text-gray-500">{{ emp.id_number || '—' }}</div>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <span class="inline-flex items-center justify-center bg-purple-50 text-purple-700 px-2.5 py-0.5 rounded-full text-xs font-semibold">{{ emp.booking_count }}</span>
                            </td>
                            <td class="px-6 py-4 text-right font-medium text-gray-800">
                                ₹{{ (emp.total_spent || 0).toLocaleString() }}
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button @click.stop="$router.push('/employees/' + emp.id)" class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors" title="View">
                                        <i class='bx bx-show text-lg'></i>
                                    </button>
                                    <button @click.stop="openModal(emp, 'edit')" class="p-1.5 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded transition-colors" title="Edit">
                                        <i class='bx bx-edit text-lg'></i>
                                    </button>
                                    <button v-if="emp.is_active" @click.stop="deleteEmployee(emp.id)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="Delete">
                                        <i class='bx bx-trash text-lg'></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination (Fixed) -->
            <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-100 bg-white flex items-center justify-between shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.02)] z-10 relative mt-auto">
                <span class="text-sm text-gray-500 font-medium">
                    Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalRecords) }} of {{ totalRecords }}
                </span>
                <div class="flex items-center gap-1">
                    <button @click="currentPage--" :disabled="currentPage === 1" class="px-3 py-1.5 border border-gray-200 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500/50">Prev</button>
                    <button v-for="p in totalPages" :key="p" @click="currentPage = p" :class="['px-3 py-1.5 border rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500/50', currentPage === p ? 'bg-brand-50 border-brand-200 text-brand-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50']">
                        {{ p }}
                    </button>
                    <button @click="currentPage++" :disabled="currentPage === totalPages" class="px-3 py-1.5 border border-gray-200 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500/50">Next</button>
                </div>
            </div>

            <!-- Create / Edit Modal -->
            <Teleport to="body">
                <Transition name="modal">
                    <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center">
                        <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModal"></div>
                        <div class="modal-container bg-white rounded-xl shadow-xl border border-gray-100 w-full max-w-lg relative z-10 overflow-hidden flex flex-col max-h-[90vh]">
                            
                            <!-- Modal Header -->
                            <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                                <h3 class="text-lg font-bold text-gray-800">{{ isViewing ? 'Employee Profile' : (isEditing ? 'Edit Employee' : 'Register New Employee') }}</h3>
                                <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><i class='bx bx-x text-2xl'></i></button>
                            </div>

                            <div class="p-6 overflow-y-auto flex-1 h-full">
                                <form v-if="!isViewing" @submit.prevent="saveEmployee" class="space-y-4">
                                    <div class="grid grid-cols-2 gap-4">
                                        <div class="col-span-2">
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Full Name *</label>
                                            <input type="text" v-model="formData.name" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-brand-500/30 outline-none">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Phone *</label>
                                            <input type="text" v-model="formData.phone" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-brand-500/30 outline-none">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Email</label>
                                            <input type="email" v-model="formData.email" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none">
                                        </div>
                                    </div>
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Company</label>
                                            <select v-model="formData.company_id" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 bg-white">
                                                <option :value="null">Independent / Individual</option>
                                                <option v-for="c in companiesOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Designation</label>
                                            <input type="text" v-model="formData.designation" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none">
                                        </div>
                                    </div>

                                    <fieldset class="border border-gray-100 rounded-lg p-3 pt-0">
                                        <legend class="px-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest">Identification</legend>
                                        <div class="grid grid-cols-2 gap-4 mt-2">
                                            <div>
                                                <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">ID Type</label>
                                                <select v-model="formData.id_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 bg-white">
                                                    <option value="">-- Select --</option>
                                                    <option value="Aadhaar">Aadhaar</option>
                                                    <option value="PAN">PAN</option>
                                                    <option value="Passport">Passport</option>
                                                    <option value="Voter ID">Voter ID</option>
                                                    <option value="DL">DL</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">ID Number</label>
                                                <input type="text" v-model="formData.id_number" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500">
                                            </div>
                                        </div>
                                    </fieldset>

                                    <div v-if="isEditing" class="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                                        <input type="checkbox" v-model="formData.is_active" id="emp_active">
                                        <label for="emp_active" class="text-sm text-gray-700">Employee is Active</label>
                                    </div>
                                </form>

                                <div v-else class="space-y-6">
                                    <div class="grid grid-cols-2 gap-x-8 gap-y-4">
                                        <div><span class="block text-[10px] font-bold text-gray-400 uppercase">Company</span><p class="text-sm font-medium">{{ formData.company_name || 'Individual' }}</p></div>
                                        <div><span class="block text-[10px] font-bold text-gray-400 uppercase">Designation</span><p class="text-sm font-medium">{{ formData.designation || 'Staff' }}</p></div>
                                        <div><span class="block text-[10px] font-bold text-gray-400 uppercase">Identification</span><p class="text-sm">{{ formData.id_type || 'None' }}: {{ formData.id_number || '—' }}</p></div>
                                    </div>

                                    <h4 class="text-sm font-semibold text-gray-800 border-b border-gray-100 pb-2 mb-3">Recent Bookings</h4>
                                    <div class="overflow-x-auto border border-gray-200 rounded-lg">
                                        <table class="w-full text-left bg-white text-sm whitespace-nowrap">
                                            <thead class="bg-gray-50/50 text-gray-500">
                                                <tr>
                                                    <th class="px-4 py-2 font-medium">Type</th>
                                                    <th class="px-4 py-2 font-medium">Date</th>
                                                    <th class="px-4 py-2 font-medium">Route/Item</th>
                                                    <th class="px-4 py-2 font-medium">Cost</th>
                                                </tr>
                                            </thead>
                                            <tbody class="divide-y divide-gray-100">
                                                <tr v-for="b in viewingBookings" :key="b.booking_id" class="hover:bg-gray-50/50">
                                                    <td class="px-4 py-2 font-medium text-gray-800">{{ b.booking_type }}</td>
                                                    <td class="px-4 py-2">{{ new Date(b.booking_date).toLocaleDateString() }}</td>
                                                    <td class="px-4 py-2">
                                                        <div class="text-xs text-gray-700">
                                                            <span v-if="b.booking_type === 'Hotel'">{{ b.hotel_name }} - {{ b.from_city }}</span>
                                                            <span v-else>{{ b.from_city }} <i class='bx bx-right-arrow-alt text-gray-400'></i> {{ b.to_city }}</span>
                                                        </div>
                                                    </td>
                                                    <td class="px-4 py-2 font-medium text-gray-800">₹{{ b.cost.toLocaleString() }}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                                <div v-if="isViewing && viewingBookings.length === 0" class="px-6 pb-6 text-sm text-gray-500 italic">
                                    No bookings found for this employee.
                                </div>
                            </div>
                            
                            <div class="px-6 py-4 border-t border-gray-100 bg-gray-50/50 flex justify-end gap-3 rounded-b-xl">
                                <button type="button" @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-200">
                                    {{ isViewing ? 'Close' : 'Cancel' }}
                                </button>
                                <button v-if="!isViewing" type="button" @click="saveEmployee" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500/50 flex items-center gap-2 shadow-md shadow-brand-500/20">
                                    <i v-if="saving" class='bx bx-loader-alt bx-spin'></i>
                                    {{ isEditing ? 'Update Employee' : 'Register Employee' }}
                                </button>
                            </div>

                        </div>
                    </div>
                </Transition>
            </Teleport>
        </div>
    `,
    setup() {
        const employees = ref([]);
        const companiesOptions = ref([]);
        const loading = ref(true);
        const filters = reactive({
            search: '',
            company_id: '',
            sort_by: 'created_at',
            order: 'desc'
        });
        let searchTimeout;

        // Pagination State
        const currentPage = ref(1);
        const pageSize = ref(15);
        const totalRecords = ref(0);
        const totalPages = ref(0);

        const showModal = ref(false);
        const isEditing = ref(false);
        const isViewing = ref(false);
        const saving = ref(false);
        const viewingBookings = ref([]);
        const formData = reactive({
            id: null, name: '', phone: '', email: '',
            designation: '', company_id: null, id_type: '', id_number: '', is_active: true
        });

        const fetchEmployees = async () => {
            loading.value = true;
            try {
                let url = `/api/employees?search=${encodeURIComponent(filters.search)}&page=${currentPage.value}&size=${pageSize.value}`;
                if (filters.company_id) url += `&company_id=${filters.company_id}`;
                if (filters.sort_by) url += `&sort_by=${filters.sort_by}`;
                if (filters.order) url += `&order=${filters.order}`;
                const res = await api.request(url);
                employees.value = res.items;
                totalRecords.value = res.total;
                totalPages.value = res.pages;
            } catch (error) { }
            finally {
                loading.value = false;
            }
        };

        const fetchCompanies = async () => {
            try {
                // Fetch all companies for the dropdown (high limit for now)
                const res = await api.request(`/api/companies?size=200`);
                companiesOptions.value = res.items || [];
            } catch (e) { }
        };

        const debouncedFetch = () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage.value = 1;
                fetchEmployees();
            }, 300);
        };

        watch(currentPage, fetchEmployees);
        watch(() => filters.company_id, () => {
            currentPage.value = 1;
            fetchEmployees();
        });

        const openModal = async (emp = null, mode = 'edit') => {
            isViewing.value = mode === 'view';
            viewingBookings.value = [];
            if (emp) {
                const sanitizedEmp = { ...emp };
                for (let key in sanitizedEmp) {
                    if (sanitizedEmp[key] === null && key !== 'company_id') sanitizedEmp[key] = '';
                }
                Object.assign(formData, sanitizedEmp);
                if (mode === 'view') {
                    try {
                        const res = await api.request(`/api/employees/${emp.id}/bookings`);
                        viewingBookings.value = res.bookings || [];
                    } catch (e) { }
                }
            } else {
                isEditing.value = false;
                Object.assign(formData, { id: null, name: '', phone: '', email: '', designation: '', company_id: null, id_type: '', id_number: '', is_active: true });
            }
            showModal.value = true;
        };

        const closeModal = () => showModal.value = false;

        const saveEmployee = async () => {
            if (!formData.name || !formData.phone) return appState.showToast('Name and phone are required', 'error');
            saving.value = true;
            try {
                if (isEditing.value) {
                    await api.request(`/api/employees/${formData.id}`, { method: 'PUT', body: formData });
                    appState.showToast('Employee updated successfully');
                } else {
                    await api.request('/api/employees', { method: 'POST', body: formData });
                    appState.showToast('Employee registered successfully');
                }
                closeModal();
                fetchEmployees();
            } catch (e) { }
            finally {
                saving.value = false;
            }
        };

        const deleteEmployee = async (id) => {
            if (!confirm('Are you sure you want to delete this employee?')) return;
            try {
                await api.request(`/api/employees/${id}`, { method: 'DELETE' });
                appState.showToast('Employee deleted (Soft delete)');
                fetchEmployees();
            } catch (e) { }
        };

        onMounted(() => {
            fetchEmployees();
            fetchCompanies();
        });

        return {
            employees, companiesOptions, loading, filters, debouncedFetch,
            currentPage, pageSize, totalPages, totalRecords,
            showModal, isEditing, isViewing, viewingBookings, saving, formData,
            openModal, closeModal, saveEmployee, deleteEmployee
        };
    }
});
