const CompaniesView = defineComponent({
    template: `
        <div class="space-y-6">
            <!-- Header Actions -->
            <div class="premium-card p-4 rounded-2xl flex flex-col lg:flex-row justify-between lg:items-center gap-4">
                <div class="flex flex-wrap items-center gap-4 flex-1">
                    <div class="relative min-w-[260px]">
                        <i class='bx bx-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl'></i>
                        <input type="text" v-model="filters.search" @input="debouncedFetch" placeholder="Search by name, GST, contact..." 
                               class="w-full pl-12 pr-4 py-2.5 bg-gray-50 border-none rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:bg-white transition-all font-medium placeholder-gray-400 shadow-sm">
                    </div>
                    
                    <div class="flex items-center gap-2 bg-gray-50 p-1 rounded-xl border border-gray-100/50 flex-wrap">
                        <select v-model="filters.sort_by" @change="fetchCompanies" class="bg-transparent border-none text-[10px] font-black uppercase tracking-tighter text-gray-400 py-1.5 px-3 focus:ring-0 cursor-pointer">
                            <option value="created_at">Onboard Date</option>
                            <option value="name">Company Name</option>
                        </select>
                        <button @click="filters.order = filters.order === 'asc' ? 'desc' : 'asc'; fetchCompanies()" 
                                class="w-8 h-8 flex items-center justify-center bg-white rounded-lg text-gray-400 hover:text-brand-600 shadow-sm transition-all active:scale-95">
                            <i :class="['bx text-lg', filters.order === 'asc' ? 'bx-sort-a-z' : 'bx-sort-z-a']"></i>
                        </button>
                    </div>
                </div>
                <button @click="openModal()" class="bg-brand-600 hover:bg-brand-700 text-white pl-4 pr-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-brand-500/20 flex items-center gap-2 shrink-0 active:scale-95">
                    <i class='bx bx-plus-circle text-xl'></i> Add Company
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
                            <th class="px-6 py-4">Company Name</th>
                            <th class="px-6 py-4">Contact</th>
                            <th class="px-6 py-4 text-center">Employees</th>
                            <th class="px-6 py-4 text-center">Bookings</th>
                            <th class="px-6 py-4 text-right">Total Spent</th>
                            <th class="px-6 py-4 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 text-sm">
                        <tr v-if="!companies || companies.length === 0">
                            <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                                <div class="flex flex-col items-center justify-center">
                                    <i class='bx bx-buildings text-4xl text-gray-300 mb-2'></i>
                                    <p>No companies found.</p>
                                </div>
                            </td>
                        </tr>
                        <tr v-for="company in companies" :key="company.id" @click="$router.push('/companies/' + company.id)" class="hover:bg-gray-50/50 transition-colors group bg-white cursor-pointer">
                            <td class="px-6 py-4">
                                <div class="font-medium text-gray-900 flex items-center gap-2">
                                    {{ company.name }}
                                    <span v-if="!company.is_active" class="px-1.5 py-0.5 rounded bg-gray-100 text-[10px] text-gray-400 uppercase font-bold">Deleted</span>
                                </div>
                                <div class="text-xs text-gray-500 mt-0.5">{{ company.industry || 'N/A' }} • GST: {{ company.gst_number || 'N/A' }}</div>
                            </td>
                            <td class="px-6 py-4">
                                <div v-if="company.email" class="flex items-center gap-1.5 text-gray-600 mb-1"><i class='bx bx-envelope text-gray-400'></i>{{ company.email }}</div>
                                <div v-if="company.phone" class="flex items-center gap-1.5 text-gray-600"><i class='bx bx-phone text-gray-400'></i>{{ company.phone }}</div>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <span class="inline-flex items-center justify-center bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded-full text-xs font-semibold">{{ company.employee_count }}</span>
                            </td>
                            <td class="px-6 py-4 text-center">
                                <span class="inline-flex items-center justify-center bg-purple-50 text-purple-700 px-2.5 py-0.5 rounded-full text-xs font-semibold">{{ company.booking_count }}</span>
                            </td>
                            <td class="px-6 py-4 text-right font-medium text-gray-800">
                                ₹{{ (company.total_spent || 0).toLocaleString() }}
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button @click.stop="$router.push('/companies/' + company.id)" class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors" title="View">
                                        <i class='bx bx-show text-lg'></i>
                                    </button>
                                    <button @click.stop="openModal(company, 'edit')" class="p-1.5 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded transition-colors" title="Edit">
                                        <i class='bx bx-edit text-lg'></i>
                                    </button>
                                    <button v-if="company.is_active" @click.stop="deleteCompany(company.id)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="Delete">
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
                    <button @click="currentPage--" :disabled="currentPage === 1" class="px-3 py-1.5 border border-gray-200 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">Prev</button>
                    <button v-for="p in totalPages" :key="p" @click="currentPage = p" :class="['px-3 py-1.5 border rounded-md text-sm font-medium transition-colors', currentPage === p ? 'bg-brand-50 border-brand-200 text-brand-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50']">
                        {{ p }}
                    </button>
                    <button @click="currentPage++" :disabled="currentPage === totalPages" class="px-3 py-1.5 border border-gray-200 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">Next</button>
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
                                <h3 class="text-lg font-bold text-gray-800">{{ isViewing ? 'Company Profile' : (isEditing ? 'Edit Company' : 'Register New Company') }}</h3>
                                <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><i class='bx bx-x text-2xl'></i></button>
                            </div>

                            <div class="p-6 overflow-y-auto flex-1 h-full">
                                <form v-if="!isViewing" @submit.prevent="saveCompany" class="space-y-4">
                                    <div class="grid grid-cols-2 gap-4">
                                        <div class="col-span-2">
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Company Name *</label>
                                            <input type="text" v-model="formData.name" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-brand-500/30 outline-none">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Industry</label>
                                            <input type="text" v-model="formData.industry" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">GST Number</label>
                                            <input type="text" v-model="formData.gst_number" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none">
                                        </div>
                                    </div>
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Phone</label>
                                            <input type="text" v-model="formData.phone" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Email</label>
                                            <input type="email" v-model="formData.email" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none">
                                        </div>
                                    </div>
                                    <div>
                                        <label class="block text-xs font-semibold text-gray-600 uppercase mb-1">Address</label>
                                        <textarea v-model="formData.address" rows="3" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none resize-none"></textarea>
                                    </div>
                                    <div v-if="isEditing" class="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                                        <input type="checkbox" v-model="formData.is_active" id="is_active">
                                        <label for="is_active" class="text-sm text-gray-700">Company is Active</label>
                                    </div>
                                </form>

                                <div v-else class="space-y-6">
                                    <div class="grid grid-cols-2 gap-x-8 gap-y-4">
                                        <div><span class="block text-[10px] font-bold text-gray-400 uppercase">Industry</span><p class="text-sm font-medium">{{ formData.industry || 'General' }}</p></div>
                                        <div><span class="block text-[10px] font-bold text-gray-400 uppercase">GST Registration</span><p class="text-sm font-medium">{{ formData.gst_number || 'Not Provided' }}</p></div>
                                        <div class="col-span-2 p-3 bg-gray-50 rounded-lg border border-gray-100">
                                            <span class="block text-[10px] font-bold text-gray-400 uppercase mb-1">Office Address</span>
                                            <p class="text-sm">{{ formData.address || 'No address registered' }}</p>
                                        </div>
                                    </div>

                                    <h4 class="text-sm font-semibold text-gray-800 border-b border-gray-100 pb-2 mb-3">Employees at Company</h4>
                                    <div class="overflow-hidden border border-gray-200 rounded-lg">
                                        <table class="w-full text-left bg-white text-sm">
                                            <thead class="bg-gray-50/50 text-gray-500">
                                                <tr>
                                                    <th class="px-4 py-2 font-medium">Name</th>
                                                    <th class="px-4 py-2 font-medium">Contact</th>
                                                    <th class="px-4 py-2 font-medium">Bookings</th>
                                                    <th class="px-4 py-2 font-medium">Total Spent</th>
                                                </tr>
                                            </thead>
                                            <tbody class="divide-y divide-gray-100">
                                                <tr v-for="emp in viewingEmployees" :key="emp.id" class="hover:bg-gray-50/50">
                                                    <td class="px-4 py-2 font-medium text-gray-800">{{ emp.name }}</td>
                                                    <td class="px-4 py-2">
                                                        <div class="text-gray-900">{{ emp.phone }}</div>
                                                        <div class="text-xs text-gray-500">{{ emp.email }}</div>
                                                    </td>
                                                    <td class="px-4 py-2 text-center">
                                                        <span class="inline-flex items-center justify-center bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full text-xs font-semibold">{{ emp.booking_count }}</span>
                                                    </td>
                                                    <td class="px-4 py-2 font-medium text-gray-800 text-right">₹{{ (emp.total_spent || 0).toLocaleString() }}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                                <div v-if="isViewing && viewingEmployees.length === 0" class="px-6 pb-6 text-sm text-gray-500 italic">
                                    No employees found for this company.
                                </div>
                            </div>
                            
                            <!-- Modal Footer -->
                            <div class="px-6 py-4 border-t border-gray-100 bg-gray-50/50 flex justify-end gap-3 rounded-b-xl">
                                <button type="button" @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-200">
                                    {{ isViewing ? 'Close' : 'Cancel' }}
                                </button>
                                <button v-if="!isViewing" type="button" @click="saveCompany" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500/50 flex items-center gap-2 shadow-md shadow-brand-500/20">
                                    <i v-if="saving" class='bx bx-loader-alt bx-spin'></i>
                                    {{ isEditing ? 'Update Company' : 'Create Company' }}
                                </button>
                            </div>

                        </div>
                    </div>
                </Transition>
            </Teleport>
        </div>
    `,
    setup() {
        const companies = ref([]);
        const loading = ref(true);
        const filters = reactive({
            search: '',
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
        const viewingEmployees = ref([]);
        const formData = reactive({ id: null, name: '', industry: '', phone: '', email: '', address: '', gst_number: '', is_active: true });

        const fetchCompanies = async () => {
            loading.value = true;
            try {
                let url = `/api/companies?search=${encodeURIComponent(filters.search)}&page=${currentPage.value}&size=${pageSize.value}`;
                if (filters.sort_by) url += `&sort_by=${filters.sort_by}`;
                if (filters.order) url += `&order=${filters.order}`;
                const res = await api.request(url);
                companies.value = res.items;
                totalRecords.value = res.total;
                totalPages.value = res.pages;
            } catch (error) {
            } finally {
                loading.value = false;
            }
        };

        const debouncedFetch = () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage.value = 1; // Reset to first page on new search
                fetchCompanies();
            }, 300);
        };

        watch(currentPage, fetchCompanies);

        const openModal = async (company = null, mode = 'edit') => {
            isViewing.value = mode === 'view';
            viewingEmployees.value = [];
            if (company) {
                isEditing.value = mode === 'edit';
                Object.assign(formData, company);
                if (mode === 'view') {
                    try {
                        const res = await api.request(`/api/companies/${company.id}/details`);
                        viewingEmployees.value = res.employees || [];
                    } catch (e) { }
                }
            } else {
                isEditing.value = false;
                Object.assign(formData, { id: null, name: '', industry: '', phone: '', email: '', address: '', gst_number: '', is_active: true });
            }
            showModal.value = true;
        };

        const closeModal = () => showModal.value = false;

        const saveCompany = async () => {
            if (!formData.name) return appState.showToast('Company name is required', 'error');
            saving.value = true;
            try {
                if (isEditing.value) {
                    await api.request(`/api/companies/${formData.id}`, { method: 'PUT', body: formData });
                    appState.showToast('Company updated successfully');
                } else {
                    await api.request('/api/companies', { method: 'POST', body: formData });
                    appState.showToast('Company registered successfully');
                }
                closeModal();
                fetchCompanies();
            } catch (e) {
            } finally {
                saving.value = false;
            }
        };

        const deleteCompany = async (id) => {
            if (!confirm('Are you sure you want to delete this company?')) return;
            try {
                await api.request(`/api/companies/${id}`, { method: 'DELETE' });
                appState.showToast('Company deleted (Soft delete)');
                fetchCompanies();
            } catch (e) { }
        };

        onMounted(fetchCompanies);

        return {
            companies, loading, filters, debouncedFetch,
            currentPage, pageSize, totalPages, totalRecords,
            showModal, isEditing, isViewing, viewingEmployees, saving, formData,
            openModal, closeModal, saveCompany, deleteCompany
        };
    }
});
