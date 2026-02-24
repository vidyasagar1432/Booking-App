const BookingsView = defineComponent({
    template: `
        <div class="space-y-6">
            <!-- Header Actions -->
            <div class="premium-card p-4 rounded-2xl flex flex-col lg:flex-row justify-between lg:items-center gap-4">
                <div class="flex flex-wrap items-center gap-4 flex-1">
                    <div class="relative min-w-[260px]">
                        <i class='bx bx-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-xl'></i>
                        <input type="text" v-model="filters.search" @input="debouncedFetch" placeholder="Search by ID, route, PNR..." 
                               class="w-full pl-12 pr-4 py-2.5 bg-gray-50 border-none rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:bg-white transition-all font-medium placeholder-gray-400 shadow-sm">
                    </div>
                    
                    <div class="flex items-center gap-2 bg-gray-50 p-1 rounded-xl border border-gray-100/50 flex-wrap">
                        <select v-model="filters.type" @change="fetchBookings" class="bg-transparent border-none text-xs font-bold uppercase tracking-wider text-gray-500 py-1.5 px-3 focus:ring-0 cursor-pointer hover:bg-white rounded-lg transition-colors">
                            <option value="">All Types</option>
                            <option value="Flight">Flight</option>
                            <option value="Train">Train</option>
                            <option value="Bus">Bus</option>
                            <option value="Hotel">Hotel</option>
                        </select>
                        <span class="w-px h-4 bg-gray-200 mx-1"></span>
                        <select v-model="filters.status" @change="fetchBookings" class="bg-transparent border-none text-xs font-bold uppercase tracking-wider text-gray-500 py-1.5 px-3 focus:ring-0 cursor-pointer hover:bg-white rounded-lg transition-colors">
                            <option value="">Status</option>
                            <option value="Confirmed">Confirmed</option>
                            <option value="Pending">Pending</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                        <span class="w-px h-4 bg-gray-200 mx-1"></span>
                        <div class="flex items-center gap-1.5 px-2">
                             <input type="date" v-model="filters.date_from" @change="fetchBookings" class="bg-transparent border-none text-xs font-bold text-gray-500 p-0 w-24 focus:ring-0">
                             <span class="text-gray-300">/</span>
                             <input type="date" v-model="filters.date_to" @change="fetchBookings" class="bg-transparent border-none text-xs font-bold text-gray-500 p-0 w-24 focus:ring-0">
                        </div>
                    </div>

                    <div class="flex items-center gap-2 bg-gray-50 p-1 rounded-xl border border-gray-100/50">
                        <select v-model="filters.sort_by" @change="fetchBookings" class="bg-transparent border-none text-[10px] font-black uppercase tracking-tighter text-gray-400 py-1.5 px-2 focus:ring-0 cursor-pointer">
                            <option value="booking_date">Reg Date</option>
                            <option value="cost">Total Cost</option>
                            <option value="booking_id">Booking ID</option>
                            <option value="status">Booking Status</option>
                        </select>
                        <button @click="filters.order = filters.order === 'asc' ? 'desc' : 'asc'; fetchBookings()" 
                                class="w-8 h-8 flex items-center justify-center bg-white rounded-lg text-gray-400 hover:text-brand-600 shadow-sm transition-all active:scale-95">
                            <i :class="['bx text-lg', filters.order === 'asc' ? 'bx-sort-a-z' : 'bx-sort-z-a']"></i>
                        </button>
                    </div>
                </div>
                <button @click="openModal()" class="bg-brand-600 hover:bg-brand-700 text-white pl-4 pr-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-brand-500/20 flex items-center gap-2 shrink-0 active:scale-95">
                    <i class='bx bx-plus-circle text-xl'></i> New Booking
                </button>
            </div>

            <!-- List Table Container -->
            <div class="premium-card rounded-2xl overflow-hidden animate-fade-in">
                <div v-if="loading" class="flex justify-center items-center h-32 text-brand-600">
                    <i class='bx bx-loader-alt bx-spin text-2xl'></i>
                </div>
                
                <div v-else class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead class="sticky top-0 bg-gray-50/95 backdrop-blur-sm z-10 shadow-sm">
                            <tr class="border-b border-gray-100 text-xs uppercase tracking-wider text-gray-500 font-semibold">
                                <th class="px-6 py-4">Booking ID</th>
                                <th class="px-6 py-4">Type & Route</th>
                                <th class="px-6 py-4">Dates</th>
                                <th class="px-6 py-4">Passengers</th>
                                <th class="px-6 py-4 text-center">Status</th>
                                <th class="px-6 py-4 text-right">Cost</th>
                                <th class="px-6 py-4 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm">
                            <tr v-if="!bookings || bookings.length === 0">
                                <td colspan="7" class="px-6 py-12 text-center text-gray-500 bg-white">
                                    <div class="flex flex-col items-center justify-center">
                                        <i class='bx bx-book-content text-5xl text-gray-200 mb-3'></i>
                                        <p class="text-base font-medium text-gray-600">No bookings found</p>
                                        <p class="text-xs text-gray-400 mt-1">Try adjusting your filters or create a new booking.</p>
                                    </div>
                                </td>
                            </tr>
                            <tr v-for="b in bookings" :key="b.booking_id" @click="$router.push('/bookings/' + b.booking_id)" class="hover:bg-gray-50/50 transition-colors group bg-white cursor-pointer">
                                <td class="px-6 py-4">
                                    <div class="font-medium text-brand-700 font-mono">{{ b.booking_id }}</div>
                                    <div class="text-xs text-gray-500 mt-0.5">{{ formatDateTime(b.booking_date) }}</div>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-2 mb-1">
                                        <span :class="getTypeBadgeClass(b.booking_type)">
                                            <i :class="getTypeIcon(b.booking_type)"></i> {{ b.booking_type }}
                                        </span>
                                    </div>
                                    <div class="text-gray-700 font-medium text-xs flex items-center gap-1">
                                        <template v-if="b.booking_type !== 'Hotel'">
                                            {{ b.from_city }} <i class='bx bx-right-arrow-alt text-gray-400'></i> {{ b.to_city }}
                                        </template>
                                        <template v-else>
                                            {{ b.hotel_name || b.from_city || 'Unnamed Hotel' }}
                                        </template>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="text-gray-900 text-[11px] mb-1 whitespace-nowrap"><span class="text-gray-400 w-8 inline-block uppercase font-bold text-[9px]">Start</span> {{ formatDateTime(b.start_datetime) }}</div>
                                    <div class="text-gray-900 text-[11px] whitespace-nowrap"><span class="text-gray-400 w-8 inline-block uppercase font-bold text-[9px]">End</span> {{ formatDateTime(b.end_datetime) }}</div>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="flex -space-x-2 overflow-hidden items-center group/avatars">
                                        <div v-for="(emp, i) in b.employees.slice(0, 3)" :key="emp.id" 
                                             class="inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gradient-to-tr from-brand-100 to-brand-200 text-brand-700 flex items-center justify-center text-xs font-bold shadow-sm"
                                             :title="emp.name">
                                            {{ emp.name.charAt(0) }}
                                        </div>
                                        <div v-if="b.employees.length > 3" class="inline-block h-8 w-8 rounded-full ring-2 ring-white bg-gray-100 text-gray-600 flex items-center justify-center text-xs font-bold shadow-sm z-10">
                                            +{{ b.employees.length - 3 }}
                                        </div>
                                    </div>
                                    <div class="text-[10px] text-gray-400 mt-1 font-medium">{{ b.employees[0]?.name }}{{ b.employees.length > 1 ? ' + ' + (b.employees.length - 1) + ' more' : '' }}</div>
                                </td>
                                <td class="px-6 py-4 text-center">
                                    <span :class="getStatusBadgeClass(b.status)">{{ b.status }}</span>
                                </td>
                                <td class="px-6 py-4 text-right">
                                    <div class="font-bold text-gray-900">₹{{ b.cost.toLocaleString() }}</div>
                                </td>
                                <td class="px-6 py-4 text-center">
                                    <div class="flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button @click.stop="$router.push('/bookings/' + b.booking_id)" class="p-1.5 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded transition-colors" title="View Detail">
                                            <i class='bx bx-right-top-arrow-circle text-lg'></i>
                                        </button>
                                        <button @click.stop="deleteBooking(b.booking_id)" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="Delete">
                                            <i class='bx bx-trash text-lg'></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- Pagination (Improved) -->
                <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-100 bg-white flex items-center justify-between">
                    <span class="text-sm text-gray-500 font-medium whitespace-nowrap">
                        Showing <span class="text-gray-900">{{ (currentPage - 1) * pageSize + 1 }}</span> to 
                        <span class="text-gray-900">{{ Math.min(currentPage * pageSize, totalRecords) }}</span> 
                        of <span class="text-gray-900">{{ totalRecords }}</span>
                    </span>
                    <div class="flex items-center gap-1">
                        <button @click="currentPage--" :disabled="currentPage === 1" class="px-3 py-1.5 border border-gray-200 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors">Prev</button>
                        <button v-for="p in totalPages" :key="p" @click="currentPage = p" :class="['px-3 py-1.5 border rounded-md text-sm font-medium transition-colors', currentPage === p ? 'bg-brand-50 border-brand-200 text-brand-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50']">
                            {{ p }}
                        </button>
                        <button @click="currentPage++" :disabled="currentPage === totalPages" class="px-3 py-1.5 border border-gray-200 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors">Next</button>
                    </div>
                </div>
            </div>

            <!-- Booking Modal (Create/Edit) -->
            <Teleport to="body">
                <Transition name="modal">
                    <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
                        <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="closeModal"></div>
                        <div class="modal-container bg-white rounded-2xl shadow-2xl border border-gray-100 w-full max-w-5xl relative z-10 overflow-hidden flex flex-col max-h-[95vh] animate-in fade-in zoom-in duration-200">
                            
                            <!-- Header -->
                            <div class="px-8 py-5 border-b border-gray-100 flex justify-between items-center bg-white">
                                <div>
                                    <h3 class="text-xl font-bold text-gray-800">{{ isEditing ? 'Edit Booking' : 'New Booking Registration' }}</h3>
                                    <p class="text-xs text-gray-500 mt-0.5">Enter the travel details and passenger information below.</p>
                                </div>
                                <button @click="closeModal" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-full transition-colors"><i class='bx bx-x text-2xl'></i></button>
                            </div>

                            <!-- Form Content -->
                            <div class="p-8 overflow-y-auto flex-1 h-full scrollbar-thin">
                                <form @submit.prevent="saveBooking" class="space-y-8">
                                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
                                        
                                        <!-- Column 1: Core Details -->
                                        <div class="lg:col-span-7 space-y-6">
                                            
                                             <!-- Step 1: Booking Type & Date -->
                                             <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                 <div>
                                                     <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3">1. Select Service Type</label>
                                                     <div class="grid grid-cols-4 gap-3">
                                                         <button v-for="t in ['Flight', 'Train', 'Bus', 'Hotel']" :key="t" 
                                                                 type="button" 
                                                                 @click="formData.booking_type = t"
                                                                 :class="['flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all group', formData.booking_type === t ? 'border-brand-500 bg-brand-50/50 text-brand-700 shadow-sm' : 'border-gray-100 hover:border-brand-200 hover:bg-gray-50 text-gray-500']">
                                                             <i class='text-2xl mb-1' :class="getTypeIcon(t)"></i>
                                                             <span class="text-[11px] font-bold uppercase tracking-wider">{{ t }}</span>
                                                         </button>
                                                     </div>
                                                 </div>
                                                 <div>
                                                     <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3">Booking Date & Time</label>
                                                     <input type="datetime-local" v-model="formData.booking_date" class="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 outline-none transition-all">
                                                 </div>
                                             </div>

                                            <div class="h-px bg-gray-100 w-full"></div>

                                            <!-- Step 2: Route & Times -->
                                            <div class="space-y-4">
                                                <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-1">2. Journey & Routing</label>
                                                <div class="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">{{ formData.booking_type === 'Hotel' ? 'City' : 'Origin City' }}</label>
                                                        <autocomplete-input field="from_city" v-model="formData.from_city" placeholder="e.g. Mumbai" inputClass="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 outline-none transition-all" />
                                                    </div>
                                                    <div v-if="formData.booking_type !== 'Hotel'">
                                                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">Destination City</label>
                                                        <autocomplete-input field="to_city" v-model="formData.to_city" placeholder="e.g. Delhi" inputClass="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 outline-none transition-all" />
                                                    </div>
                                                </div>

                                                <div class="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">{{ formData.booking_type === 'Hotel' ? 'Check-in' : 'Departure Time' }}</label>
                                                        <input type="datetime-local" v-model="formData.start_datetime" class="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 outline-none transition-all">
                                                    </div>
                                                    <div>
                                                        <label class="block text-xs font-semibold text-gray-600 mb-1.5">{{ formData.booking_type === 'Hotel' ? 'Check-out' : 'Arrival Time' }}</label>
                                                        <input type="datetime-local" v-model="formData.end_datetime" class="w-full px-4 py-2.5 bg-gray-50/50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500/20 outline-none transition-all">
                                                    </div>
                                                </div>
                                            </div>

                                            <!-- Step 3: Type Specific (Dynamic) -->
                                            <div class="p-6 bg-gray-50 rounded-2xl border border-gray-200/60 space-y-4">
                                                <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-1">3. {{ formData.booking_type }} Specifications</label>
                                                
                                                <!-- Flight Fields -->
                                                <div v-if="formData.booking_type === 'Flight'" class="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-1 duration-200">
                                                    <div><label class="block text-xs text-gray-500 mb-1">Airline</label><autocomplete-input field="airline" v-model="formData.airline" inputClass="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none" /></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Flight No.</label><input type="text" v-model="formData.flight_number" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">PNR Status</label><input type="text" v-model="formData.pnr_status" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Class</label><input type="text" v-model="formData.seat_class" placeholder="Economy/Business" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                </div>

                                                <!-- Similarly for Train, Bus, Hotel -->
                                                <div v-else-if="formData.booking_type === 'Train'" class="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-1 duration-200">
                                                    <div><label class="block text-xs text-gray-500 mb-1">Train No/Name</label><autocomplete-input field="train_number" v-model="formData.train_number" inputClass="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none" /></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Class</label><input type="text" v-model="formData.seat_class" placeholder="AC 3-Tier" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Coach & Seat</label><input type="text" v-model="formData.coach_number" placeholder="S2 - 42" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Platform No.</label><input type="text" v-model="formData.platform" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div class="col-span-2"><label class="block text-xs text-gray-500 mb-1">PNR Status</label><input type="text" v-model="formData.pnr_status" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                </div>

                                                <div v-else-if="formData.booking_type === 'Bus'" class="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-1 duration-200">
                                                    <div><label class="block text-xs text-gray-500 mb-1">Bus Operator</label><autocomplete-input field="bus_operator" v-model="formData.bus_operator" inputClass="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none" /></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Bus PNR</label><input type="text" v-model="formData.bus_pnr" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Pickup Point</label><input type="text" v-model="formData.pickup_point" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Drop Point</label><input type="text" v-model="formData.drop_point" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                </div>

                                                <div v-else-if="formData.booking_type === 'Hotel'" class="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-1 duration-200">
                                                    <div class="col-span-2"><label class="block text-xs text-gray-500 mb-1">Hotel Name</label><autocomplete-input field="hotel_name" v-model="formData.hotel_name" inputClass="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none" /></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Room Type</label><input type="text" v-model="formData.room_type" placeholder="Deluxe/Suite" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Address/Area</label><input type="text" v-model="formData.hotel_address" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Check-in Time</label><input type="text" v-model="formData.check_in_time" placeholder="12:00 PM" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                    <div><label class="block text-xs text-gray-500 mb-1">Check-out Time</label><input type="text" v-model="formData.check_out_time" placeholder="11:00 AM" class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm outline-none"></div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Column 2: Passengers & Finalize -->
                                        <div class="lg:col-span-5 space-y-6 flex flex-col h-full">
                                            
                                            <!-- Passengers -->
                                            <div class="flex-1 min-h-[300px] flex flex-col">
                                                <div class="flex justify-between items-center mb-4">
                                                    <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-widest">4. Passenger Details</label>
                                                    <button type="button" @click="addPassenger" class="text-[11px] font-bold text-brand-600 bg-brand-50 px-2 py-1 rounded hover:bg-brand-100 transition-colors uppercase tracking-widest flex items-center gap-1">
                                                        <i class='bx bx-plus'></i> Add More
                                                    </button>
                                                </div>
                                                
                                                <div class="space-y-4 overflow-y-auto max-h-[40vh] pr-2 pb-20 scrollbar-thin">
                                                    <div v-for="(pax, idx) in formData.employees" :key="idx" 
                                                         class="p-4 bg-white border border-gray-200 rounded-2xl relative group/pax shadow-sm hover:shadow-md hover:border-brand-200 transition-all passenger-card">
                                                        <div class="grid grid-cols-2 gap-3 mb-2">
                                                            <div>
                                                                <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">Full Name</label>
                                                                <autocomplete-input field="employee_name" v-model="pax.name" @select="(s) => autofillPassenger(pax,'name',s)" inputClass="w-full px-3 py-2 bg-gray-50/50 border border-gray-200 rounded-lg text-sm focus:bg-white outline-none" />
                                                            </div>
                                                            <div>
                                                                <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">Phone Number</label>
                                                                <autocomplete-input field="employee_phone" v-model="pax.phone" @select="(s) => autofillPassenger(pax,'phone',s)" inputClass="w-full px-3 py-2 bg-gray-50/50 border border-gray-200 rounded-lg text-sm focus:bg-white outline-none" />
                                                            </div>
                                                        </div>
                                                        <div class="flex justify-between items-center">
                                                            <div class="text-[11px] font-medium text-brand-600 flex items-center gap-1">
                                                                <i class='bx bx-building text-sm opacity-60'></i> {{ pax.company_name || 'Individual' }}
                                                            </div>
                                                            <button v-if="formData.employees.length > 1" type="button" @click="removePassenger(idx)" class="text-xs text-red-400 hover:text-red-600 flex items-center gap-1 font-semibold uppercase tracking-widest">
                                                                <i class='bx bx-trash'></i>
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            <!-- Document Vault (Upload Files before creating) -->
                                            <div class="mt-4">
                                                <div class="flex justify-between items-center mb-2">
                                                    <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-widest">5. Document Vault Attachments</label>
                                                    <label class="cursor-pointer bg-brand-50 hover:bg-brand-100 text-brand-600 px-3 py-1 rounded text-[10px] font-bold transition-colors uppercase tracking-widest flex items-center gap-1">
                                                        <i class='bx bx-upload'></i> Select Files
                                                        <input type="file" class="hidden" @change="handleFileSelect" accept=".pdf,.png,.jpg,.jpeg" multiple>
                                                    </label>
                                                </div>
                                                <div v-if="selectedFiles.length > 0" class="space-y-2 mt-2">
                                                    <div v-for="(file, idx) in selectedFiles" :key="idx" class="flex items-center justify-between p-2 pl-3 bg-gray-50 border border-gray-200 rounded-lg text-sm">
                                                        <div class="flex items-center gap-2 truncate">
                                                            <i class='bx text-gray-400 text-lg' :class="file.name.endsWith('.pdf') ? 'bxs-file-pdf text-red-400' : 'bxs-file-image'"></i>
                                                            <span class="truncate font-medium text-gray-700 max-w-[200px]">{{ file.name }}</span>
                                                        </div>
                                                        <button type="button" @click="selectedFiles.splice(idx, 1)" class="text-red-400 hover:text-red-600 p-1">
                                                            <i class='bx bx-x text-lg'></i>
                                                        </button>
                                                    </div>
                                                </div>
                                                <div v-else class="text-center p-4 border-2 border-dashed border-gray-200 rounded-xl bg-gray-50 text-gray-400 text-xs font-semibold">
                                                    <i class='bx bx-cloud-upload text-2xl mb-1 block'></i>
                                                    No documents selected
                                                </div>
                                            </div>

                                            <!-- Summary & Actions -->
                                            <div class="bg-gray-900 rounded-3xl p-6 text-white shadow-xl mt-auto">
                                                <div class="grid grid-cols-2 gap-6 mb-6">
                                                    <div>
                                                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Booking Status</label>
                                                        <select v-model="formData.status" class="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-sm focus:ring-1 focus:ring-brand-500 outline-none">
                                                            <option value="Confirmed">Confirmed</option>
                                                            <option value="Pending">Pending</option>
                                                            <option value="Completed">Completed</option>
                                                            <option value="Cancelled">Cancelled</option>
                                                        </select>
                                                    </div>
                                                    <div>
                                                        <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Total Cost (₹)</label>
                                                        <input type="number" v-model="formData.cost" class="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-lg font-bold focus:ring-1 focus:ring-brand-500 outline-none">
                                                    </div>
                                                </div>
                                                <div class="mb-6">
                                                    <label class="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Internal Notes</label>
                                                    <textarea v-model="formData.notes" placeholder="Any internal remarks or special requests..." class="w-full bg-gray-800 border border-gray-700 rounded-xl px-3 py-2 text-sm h-20 resize-none outline-none focus:ring-1 focus:ring-brand-500"></textarea>
                                                </div>
                                                <div class="flex gap-3">
                                                    <button type="button" @click="closeModal" class="flex-1 px-4 py-3 rounded-2xl border border-gray-700 font-semibold text-sm hover:bg-gray-800 transition-colors">Cancel</button>
                                                    <button type="submit" :disabled="saving" class="flex-[2] bg-brand-500 hover:bg-brand-600 px-4 py-3 rounded-2xl font-bold text-sm transition-all shadow-lg shadow-brand-500/20 flex items-center justify-center gap-2">
                                                        <i v-if="saving" class='bx bx-loader-alt bx-spin text-lg'></i>
                                                        <i v-else class='bx bx-check-double text-lg'></i>
                                                        {{ isEditing ? 'Update Booking' : 'Finalize & Book' }}
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </Transition>
            </Teleport>
        </div>
    `,
    setup() {
        const route = VueRouter.useRoute();
        const router = VueRouter.useRouter();
        const bookings = ref([]);
        const loading = ref(true);
        const filters = reactive({
            search: '',
            type: '',
            status: '',
            date_from: '',
            date_to: '',
            sort_by: 'booking_date',
            order: 'desc'
        });
        let searchTimeout;

        // Pagination State
        const currentPage = ref(1);
        const pageSize = ref(10);
        const totalRecords = ref(0);
        const totalPages = ref(0);

        const showModal = ref(false);
        const isEditing = ref(false);
        const isViewing = ref(false);
        const saving = ref(false);
        const selectedFiles = ref([]);

        const defaultFormData = () => ({
            booking_id: '',
            booking_type: 'Flight',
            booking_date: new Date().toISOString().slice(0, 16),
            from_city: '',
            to_city: '',
            start_datetime: '',
            end_datetime: '',
            cost: 0,
            status: 'Confirmed',
            notes: '',
            employees: [{ name: '', phone: '', email: '', company_name: '', designation: '', id_type: '', id_number: '' }],
            // dynamic specs
            airline: '', flight_number: '', pnr_status: '', seat_class: '',
            train_number: '', coach_number: '', platform: '',
            bus_operator: '', bus_pnr: '', pickup_point: '', drop_point: '',
            hotel_name: '', room_type: '', hotel_address: '',
            check_in_time: '', check_out_time: ''
        });

        const formData = reactive(defaultFormData());

        const fetchBookings = async () => {
            loading.value = true;
            try {
                let url = `/api/bookings?page=${currentPage.value}&size=${pageSize.value}`;
                if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`;
                if (filters.type) url += `&type=${filters.type}`;
                if (filters.status) url += `&status=${filters.status}`;
                if (filters.date_from) url += `&date_from=${filters.date_from}`;
                if (filters.date_to) url += `&date_to=${filters.date_to}`;
                if (filters.sort_by) url += `&sort_by=${filters.sort_by}`;
                if (filters.order) url += `&order=${filters.order}`;

                const res = await api.request(url);
                bookings.value = res.items;
                totalRecords.value = res.total;
                totalPages.value = res.pages;
            } catch (error) { }
            finally {
                loading.value = false;
            }
        };

        const debouncedFetch = () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage.value = 1;
                fetchBookings();
            }, 300);
        };

        watch(currentPage, fetchBookings);

        const formatDateTime = (isoStr) => {
            if (!isoStr) return 'N/A';
            const d = new Date(isoStr);
            return d.toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
        };

        const getStatusBadgeClass = (status) => {
            if (status === 'Confirmed') return 'inline-flex items-center justify-center bg-emerald-50 text-emerald-700 border border-emerald-200/60 px-2.5 py-1 rounded-md text-[11px] uppercase font-bold tracking-wider';
            if (status === 'Completed') return 'inline-flex items-center justify-center bg-indigo-50 text-indigo-700 border border-indigo-200/60 px-2.5 py-1 rounded-md text-[11px] uppercase font-bold tracking-wider';
            if (status === 'Pending') return 'inline-flex items-center justify-center bg-amber-50 text-amber-700 border border-amber-200/60 px-2.5 py-1 rounded-md text-[11px] uppercase font-bold tracking-wider';
            return 'inline-flex items-center justify-center bg-red-50 text-red-700 border border-red-200/60 px-2.5 py-1 rounded-md text-[11px] uppercase font-bold tracking-wider';
        };

        const getTypeBadgeClass = (type) => {
            const base = 'inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold mr-2 border';
            if (type === 'Flight') return base + ' bg-blue-50 text-blue-700 border-blue-100';
            if (type === 'Train') return base + ' bg-green-50 text-green-700 border-green-100';
            if (type === 'Bus') return base + ' bg-orange-50 text-orange-700 border-orange-100';
            return base + ' bg-purple-50 text-purple-700 border-purple-100';
        };

        const getTypeIcon = (type) => {
            if (type === 'Flight') return 'bx bxs-plane-alt';
            if (type === 'Train') return 'bx bxs-train';
            if (type === 'Bus') return 'bx bxs-bus';
            return 'bx bxs-building-house';
        };

        const openModal = (booking = null, mode = 'edit') => {
            isViewing.value = mode === 'view';
            if (booking) {
                isEditing.value = mode === 'edit';
                // Reset form with default then assign actual booking data
                const sanitizedBooking = { ...booking };
                for (let key in sanitizedBooking) {
                    if (sanitizedBooking[key] === null) sanitizedBooking[key] = '';
                }
                Object.assign(formData, defaultFormData(), sanitizedBooking);
                if (formData.booking_date) formData.booking_date = formData.booking_date.substring(0, 16);
                if (formData.start_datetime) formData.start_datetime = formData.start_datetime.substring(0, 16);
                if (formData.end_datetime) formData.end_datetime = formData.end_datetime.substring(0, 16);

                // Map employees for flat editing
                formData.employees = booking.employees.map(e => ({
                    name: e.name, phone: e.phone, email: e.email || '',
                    company_name: e.company_name || '',
                    designation: e.designation || '',
                    id_type: e.id_type || '',
                    id_number: e.id_number || ''
                }));
            } else {
                isEditing.value = false;
                Object.assign(formData, defaultFormData());
                const now = new Date();
                const start = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().substring(0, 16);
                const end = new Date(now.getTime() - now.getTimezoneOffset() * 60000 + 86400000).toISOString().substring(0, 16);
                formData.start_datetime = start;
                formData.end_datetime = end;
            }
            selectedFiles.value = []; // Reset attachments
            showModal.value = true;
        };

        const closeModal = () => {
            showModal.value = false;
            const q = { ...route.query };
            if (q.edit) { delete q.edit; router.replace({ query: q }); }
        };

        const addPassenger = () => formData.employees.push({ name: '', phone: '', email: '', company_name: '', designation: '', id_type: '', id_number: '' });
        const removePassenger = (idx) => formData.employees.splice(idx, 1);

        const handleFileSelect = (event) => {
            if (event.target.files) {
                for (let i = 0; i < event.target.files.length; i++) {
                    selectedFiles.value.push(event.target.files[i]);
                }
            }
            event.target.value = ''; // reset
        };

        const autofillPassenger = async (pax, field, value) => {
            try {
                const res = await api.request(`/api/employees?search=${encodeURIComponent(value)}`);
                // res now contains items property
                const emp = res.items.find(e => {
                    if (field === 'name') return e.name.toLowerCase() === value.toLowerCase();
                    if (field === 'phone') return e.phone === value;
                    return false;
                });
                if (emp) {
                    pax.name = emp.name;
                    pax.phone = emp.phone;
                    pax.email = emp.email || '';
                    pax.company_name = emp.company_name || '';
                    pax.designation = emp.designation || '';
                    pax.id_type = emp.id_type || '';
                    pax.id_number = emp.id_number || '';
                    appState.showToast(`Autofilled details for ${emp.name}`);
                }
            } catch (e) { }
        };

        const saveBooking = async () => {
            if (!formData.from_city || !formData.start_datetime || !formData.end_datetime) return appState.showToast('Please fill all required travel details', 'error');
            if (formData.employees.length === 0 || !formData.employees[0].name || !formData.employees[0].phone) return appState.showToast('At least one passenger required', 'error');

            saving.value = true;
            try {
                // Restructure payload for backend nested schemas
                const payload = {
                    booking_type: formData.booking_type,
                    status: formData.status,
                    cost: formData.cost,
                    notes: formData.notes,
                    employees: formData.employees.map(e => ({ ...e }))
                };

                // Add optional ID if editing
                if (isEditing.value) payload.booking_id = formData.booking_id;

                // Format dates safely
                const formatISO = (val) => {
                    if (!val) return null;
                    if (val.length === 16) val += ':00';
                    try { return new Date(val).toISOString(); } catch (e) { return null; }
                };

                payload.booking_date = formatISO(formData.booking_date);
                payload.start_datetime = formatISO(formData.start_datetime);
                payload.end_datetime = formatISO(formData.end_datetime);

                // Nest type-specific details
                const bType = formData.booking_type;
                if (bType === 'Flight') {
                    payload.flight_details = {
                        flight_number: formData.flight_number,
                        airline: formData.airline,
                        pnr_status: formData.pnr_status,
                        seat_class: formData.seat_class,
                        from_city: formData.from_city,
                        to_city: formData.to_city
                    };
                } else if (bType === 'Train') {
                    payload.train_details = {
                        train_number: formData.train_number,
                        coach_number: formData.coach_number,
                        platform: formData.platform,
                        pnr_status: formData.pnr_status,
                        seat_class: formData.seat_class,
                        from_city: formData.from_city,
                        to_city: formData.to_city
                    };
                } else if (bType === 'Bus') {
                    payload.bus_details = {
                        bus_operator: formData.bus_operator,
                        bus_pnr: formData.bus_pnr,
                        pickup_point: formData.pickup_point,
                        drop_point: formData.drop_point,
                        pnr_status: formData.pnr_status,
                        seat_class: formData.seat_class,
                        from_city: formData.from_city,
                        to_city: formData.to_city
                    };
                } else if (bType === 'Hotel') {
                    payload.hotel_details = {
                        hotel_name: formData.hotel_name,
                        room_type: formData.room_type,
                        hotel_address: formData.hotel_address,
                        check_in_time: formData.check_in_time,
                        check_out_time: formData.check_out_time,
                        city: formData.from_city
                    };
                }

                let finalBookingId = formData.booking_id;
                if (isEditing.value) {
                    await api.request(`/api/bookings/${formData.booking_id}`, { method: 'PUT', body: payload });
                    appState.showToast('Booking updated successfully');
                } else {
                    const res = await api.request('/api/bookings', { method: 'POST', body: payload });
                    finalBookingId = res.booking_id;
                    appState.showToast('Booking created successfully');
                }

                if (selectedFiles.value.length > 0 && finalBookingId) {
                    appState.showToast('Uploading ' + selectedFiles.value.length + ' document(s)...');
                    for (const file of selectedFiles.value) {
                        const docFormData = new FormData();
                        docFormData.append('file', file);
                        await api.request(`/api/documents/${finalBookingId}`, { method: 'POST', body: docFormData });
                    }
                    appState.showToast('Documents uploaded to vault', 'success');
                }

                closeModal();
                fetchBookings();
            } catch (e) { }
            finally {
                saving.value = false;
            }
        };

        const deleteBooking = async (id) => {
            if (!confirm('Are you sure you want to delete this booking?')) return;
            try {
                await api.request(`/api/bookings/${id}`, { method: 'DELETE' });
                appState.showToast('Booking deleted');
                fetchBookings();
            } catch (e) { }
        };

        onMounted(async () => {
            await fetchBookings();
            if (route.query.edit) {
                const bkToEdit = bookings.value.find(b => b.booking_id === route.query.edit);
                if (bkToEdit) openModal(bkToEdit, 'edit');
            }
            window.addEventListener('realtime-update', fetchBookings);
        });

        onUnmounted(() => {
            window.removeEventListener('realtime-update', fetchBookings);
        });

        watch(() => route.query.edit, (newEdit) => {
            if (newEdit) {
                const bkToEdit = bookings.value.find(b => b.booking_id === newEdit);
                if (bkToEdit) openModal(bkToEdit, 'edit');
            }
        });

        return {
            bookings, loading, filters, debouncedFetch, fetchBookings,
            currentPage, pageSize, totalPages, totalRecords,
            formatDateTime, getStatusBadgeClass, getTypeBadgeClass, getTypeIcon,
            showModal, isEditing, isViewing, saving, formData, selectedFiles,
            openModal, closeModal, saveBooking, deleteBooking,
            addPassenger, removePassenger, autofillPassenger, handleFileSelect
        };
    }
});
