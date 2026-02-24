const BookingDetailView = defineComponent({
    template: `
        <div>
            <!-- Header -->
            <div class="mb-6 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <button @click="$router.push('/bookings')" class="p-2 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-colors">
                        <i class='bx bx-arrow-back text-xl'></i>
                    </button>
                    <h2 class="text-2xl font-bold text-gray-800">{{ isEditing ? 'Edit Booking' : 'Booking Details' }}</h2>
                </div>
                <div v-if="booking && !isEditing" class="flex items-center gap-2">
                    <button @click="openEdit" class="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 flex items-center gap-2 transition-all shadow-md shadow-brand-500/20">
                        <i class='bx bx-edit text-lg'></i> Edit Booking
                    </button>
                    <button @click="deleteBooking" class="px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-100 rounded-lg hover:bg-red-50 flex items-center gap-2 transition-all shadow-sm">
                        <i class='bx bx-trash text-lg'></i> Delete
                    </button>
                </div>
                <div v-else-if="isEditing" class="flex items-center gap-2">
                    <button @click="isEditing = false" class="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-all">
                        Cancel
                    </button>
                    <button @click="saveEdit" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 flex items-center gap-2 transition-all shadow-md shadow-brand-500/20">
                        <i v-if="saving" class='bx bx-loader-alt bx-spin'></i>
                        <i v-else class='bx bx-save'></i>
                        Save Changes
                    </button>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="flex flex-col justify-center items-center h-64 text-brand-600">
                <i class='bx bx-loader-alt bx-spin text-4xl mb-2'></i>
                <span class="text-sm font-medium">Loading Booking...</span>
            </div>

            <div v-else-if="booking" class="space-y-6">
                <!-- VIEW MODE -->
                <div v-if="!isEditing" class="space-y-8 animate-fade-in">
                    <!-- Info Header -->
                    <div class="premium-card rounded-2xl p-8 flex flex-col md:flex-row gap-8 justify-between items-start md:items-center relative overflow-hidden">
                        <div class="absolute left-0 top-0 w-1 h-full bg-brand-500"></div>
                        <div class="z-10">
                            <div class="flex items-center gap-4 mb-3">
                                <span class="text-2xl font-black text-gray-900 tracking-tight">{{ booking.booking_id }}</span>
                                <span :class="getStatusBadgeClass(booking.status)" class="px-3.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all cursor-pointer shadow-sm active:scale-95" @click="toggleStatus(booking)">
                                    {{ booking.status }} <i class='bx bx-refresh ml-1 opacity-60'></i>
                                </span>
                            </div>
                            <div class="text-sm font-semibold text-gray-400 flex items-center gap-2">
                                <i class='bx' :class="getTypeIcon(booking.booking_type)"></i>
                                <span class="text-gray-800 font-bold">{{ booking.booking_type }}</span>
                                <span class="text-gray-300">•</span>
                                <span class="text-brand-600 bg-brand-50 px-2 py-0.5 rounded-md">{{ formatDateTime(booking.booking_date) }}</span>
                            </div>
                        </div>
                        <div class="text-right z-10 border-l border-gray-100 pl-8 h-full flex flex-col justify-center">
                            <div class="text-[10px] font-black text-gray-300 uppercase tracking-widest mb-1.5">Investment Allocation</div>
                            <div class="text-3xl font-black text-gray-900 flex items-baseline gap-1">
                                <span class="text-lg text-gray-400 font-medium tracking-tight">₹</span>
                                {{ booking.cost.toLocaleString() }}
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <!-- Journey Details -->
                        <div class="lg:col-span-2 premium-card rounded-2xl overflow-hidden">
                            <div class="px-8 py-5 border-b border-gray-100 bg-gray-50/30 flex items-center justify-between">
                                <h3 class="font-bold text-gray-800 text-sm uppercase tracking-wider flex items-center gap-2">
                                    <i class='bx bxs-directions text-brand-500 text-xl'></i> Logistical Matrix
                                </h3>
                                <div class="text-[10px] font-black text-gray-400 bg-gray-100 px-2 py-0.5 rounded-md">SECURE NODE</div>
                            </div>
                            <div class="p-8">
                                <!-- Hotel specific view -->
                                <div v-if="booking.booking_type === 'Hotel'" class="space-y-4">
                                    <div>
                                        <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Hotel Name & Location</span>
                                        <div class="text-lg font-medium text-gray-800">{{ booking.hotel_name || '-' }}</div>
                                        <div class="text-sm text-gray-500">{{ booking.hotel_address || booking.from_city || '-' }}</div>
                                    </div>
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Room Type</span>
                                            <div class="text-sm font-medium text-gray-800">{{ booking.room_type || '-' }}</div>
                                        </div>
                                        <div>
                                            <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Stay Duration</span>
                                            <div class="text-sm font-medium text-gray-800 flex flex-col gap-1">
                                                <span><i class='bx bx-calendar-check text-green-500 mr-2'></i>{{ new Date(booking.start_datetime).toLocaleDateString() }}</span>
                                                <span><i class='bx bx-calendar-x text-red-500 mr-2'></i>{{ new Date(booking.end_datetime).toLocaleDateString() }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <!-- Transit specific view (Flight, Train, Bus) -->
                                <div v-else>
                                    <div class="flex items-center justify-between mb-8 text-center md:text-left">
                                        <div class="flex-1">
                                            <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Origin</span>
                                            <div class="text-xl font-bold text-gray-800">{{ booking.from_city || '-' }}</div>
                                            <div class="text-sm text-gray-500 mt-1">{{ booking.pickup_point || 'Terminal' }}</div>
                                            <div class="text-sm font-medium text-brand-600 mt-2"><i class='bx bx-time-five mr-1'></i>{{ new Date(booking.start_datetime).toLocaleString() }}</div>
                                        </div>
                                        <div class="flex-1 flex flex-col items-center justify-center relative px-4 hidden md:flex">
                                            <div class="w-full h-px bg-gray-300 absolute top-1/2 -translate-y-1/2"></div>
                                            <div class="bg-white p-2 relative z-10 text-gray-400 border border-gray-200 rounded-full shadow-sm">
                                                <i class='bx' :class="getTypeIcon(booking.booking_type)"></i>
                                            </div>
                                        </div>
                                        <div class="flex-1 text-right">
                                            <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Destination</span>
                                            <div class="text-xl font-bold text-gray-800">{{ booking.to_city || '-' }}</div>
                                            <div class="text-sm text-gray-500 mt-1">{{ booking.drop_point || 'Station' }}</div>
                                            <div class="text-sm font-medium text-brand-600 mt-2">{{ new Date(booking.end_datetime).toLocaleString() }} <i class='bx bx-time-five ml-1'></i></div>
                                        </div>
                                    </div>
                                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-gray-100 dark:border-gray-700">
                                        <!-- Dynamic meta based on type -->
                                        <template v-if="booking.booking_type === 'Flight'">
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Airline</span><div class="text-sm font-medium text-gray-800">{{ booking.airline || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Flight No.</span><div class="text-sm font-medium text-gray-800">{{ booking.flight_number || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">PNR</span><div class="text-sm font-medium text-gray-800">{{ booking.pnr_status || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Class</span><div class="text-sm font-medium text-gray-800">{{ booking.seat_class || '-' }}</div></div>
                                        </template>
                                        <template v-if="booking.booking_type === 'Train'">
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Train No.</span><div class="text-sm font-medium text-gray-800">{{ booking.train_number || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Class</span><div class="text-sm font-medium text-gray-800">{{ booking.seat_class || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Coach/Seat</span><div class="text-sm font-medium text-gray-800">{{ booking.coach_number || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">PNR</span><div class="text-sm font-medium text-gray-800">{{ booking.pnr_status || '-' }}</div></div>
                                        </template>
                                        <template v-if="booking.booking_type === 'Bus'">
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Operator</span><div class="text-sm font-medium text-gray-800">{{ booking.bus_operator || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">Seat/Coach</span><div class="text-sm font-medium text-gray-800">{{ booking.coach_number || '-' }}</div></div>
                                            <div><span class="block text-xs text-gray-400 uppercase mb-1">PNR/TKT</span><div class="text-sm font-medium text-gray-800">{{ booking.bus_pnr || '-' }}</div></div>
                                        </template>
                                    </div>
                                    
                                    <!-- Embedded Leaflet Map -->
                                    <div v-if="booking.from_city && booking.to_city" class="mt-8 h-64 w-full rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 shadow-sm relative z-0">
                                        <div id="routeMap" class="w-full h-full z-0 bg-gray-50 dark:bg-gray-800"></div>
                                    </div>
                                </div>

                                <div v-if="booking.notes" class="mt-6 p-4 rounded-lg bg-yellow-50/50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-900/50">
                                    <span class="block text-xs font-semibold text-yellow-700 dark:text-yellow-600 uppercase tracking-wider mb-2"><i class='bx bx-note mr-1'></i>Notes / Remarks</span>
                                    <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ booking.notes }}</p>
                                </div>
                            </div>
                        </div>

                        <!-- Passengers -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden self-start">
                            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <i class='bx bx-group text-lg text-gray-400'></i>
                                    <h3 class="font-semibold text-gray-800">Passengers ({{ booking.employees.length }})</h3>
                                </div>
                            </div>
                            <div class="divide-y divide-gray-100">
                                <div v-for="emp in booking.employees" :key="emp.id" class="p-4 hover:bg-gray-50 transition-colors group cursor-pointer" @click="$router.push('/employees/' + emp.id)">
                                    <div class="flex items-center gap-3">
                                        <div class="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm">
                                            {{ emp.name.charAt(0).toUpperCase() }}
                                        </div>
                                        <div class="flex-1 min-w-0">
                                            <h4 class="text-sm font-semibold text-gray-900 group-hover:text-brand-600 truncate transition-colors">{{ emp.name }}</h4>
                                            <p class="text-xs text-gray-500 truncate">{{ emp.company_name || 'Independent' }}</p>
                                        </div>
                                    </div>
                                    <div class="mt-3 grid grid-cols-2 gap-2 text-xs">
                                        <div class="flex items-center gap-1.5 text-gray-600">
                                            <i class='bx bx-phone opacity-70'></i> {{ emp.phone }}
                                        </div>
                                        <div v-if="emp.id_type" class="flex items-center gap-1.5 text-gray-600">
                                            <i class='bx bx-id-card opacity-70'></i> {{ emp.id_type }}: {{ emp.id_number || 'HIDDEN' }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Document & Ticket Vault -->
                        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden self-start mt-6">
                            <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <i class='bx bx-archive text-lg text-gray-400'></i>
                                    <h3 class="font-semibold text-gray-800">Document Vault</h3>
                                </div>
                                <label class="cursor-pointer bg-brand-50 hover:bg-brand-100 text-brand-600 px-3 py-1.5 rounded-md text-xs font-bold transition-colors">
                                    <i class='bx bx-upload'></i> Upload
                                    <input type="file" class="hidden" @change="uploadDocument" accept=".pdf,.png,.jpg,.jpeg">
                                </label>
                            </div>
                            <div class="p-4" v-if="uploadingDoc">
                                <div class="flex items-center justify-center gap-2 text-brand-600 text-sm py-4">
                                    <i class='bx bx-loader-alt bx-spin'></i> Uploading...
                                </div>
                            </div>
                            <div class="divide-y divide-gray-100" v-else>
                                <div v-if="documents.length === 0" class="p-6 text-center text-gray-400 text-sm">
                                    <i class='bx bx-folder-open text-3xl mb-2 opacity-50 block'></i>
                                    No documents uploaded
                                </div>
                                <div v-for="doc in documents" :key="doc.filename" class="p-4 hover:bg-gray-50 transition-colors flex items-center justify-between group">
                                    <div class="flex items-center gap-3 overflow-hidden">
                                        <div class="w-8 h-8 rounded bg-gray-100 text-gray-500 flex items-center justify-center shrink-0">
                                            <i class='bx bxs-file-pdf' v-if="doc.filename.endsWith('.pdf')"></i>
                                            <i class='bx bxs-file-image' v-else></i>
                                        </div>
                                        <a href="#" @click.prevent="downloadDoc(doc)" class="text-sm font-semibold text-gray-800 group-hover:text-brand-600 truncate transition-colors" :title="doc.filename">{{ doc.filename }}</a>
                                    </div>
                                    <button @click="downloadDoc(doc)" class="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-400 hover:text-brand-600 hover:border-brand-200 transition-colors shrink-0">
                                        <i class='bx bx-download'></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- EDIT MODE -->
                <div v-else class="space-y-6">
                    <form @submit.prevent="saveEdit">
                        <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
                            
                            <!-- Left Column: Core Details -->
                            <div class="md:col-span-8 space-y-6">
                                
                                <!-- Type & Routing -->
                                <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
                                    <h4 class="text-sm font-semibold text-gray-800 mb-4 border-b border-gray-100 pb-2">Travel Details</h4>
                                    
                                    <div class="grid grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">Booking Type *</label>
                                            <div class="flex gap-2 p-1 bg-gray-50 rounded-lg border border-gray-200">
                                                <button v-for="t in ['Flight', 'Train', 'Bus', 'Hotel']" :key="t" 
                                                        type="button" 
                                                        @click="formData.booking_type = t"
                                                        :class="['flex-1 py-1.5 text-sm font-medium rounded-md transition-all', formData.booking_type === t ? 'bg-white text-brand-600 shadow-sm border' : 'text-gray-500 hover:text-gray-700']">
                                                    {{ t }}
                                                </button>
                                            </div>
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">Booking Date & Time</label>
                                            <input type="datetime-local" v-model="formData.booking_date" class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm">
                                        </div>
                                    </div>

                                    <div class="grid grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">{{ formData.booking_type === 'Hotel' ? 'City' : 'From City' }} *</label>
                                            <autocomplete-input field="from_city" v-model="formData.from_city" placeholder="Origin" inputClass="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
                                        </div>
                                        <div v-if="formData.booking_type !== 'Hotel'">
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">To City *</label>
                                            <autocomplete-input field="to_city" v-model="formData.to_city" placeholder="Destination" inputClass="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
                                        </div>
                                    </div>

                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">Start Time *</label>
                                            <input type="datetime-local" v-model="formData.start_datetime" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">End Time *</label>
                                            <input type="datetime-local" v-model="formData.end_datetime" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
                                        </div>
                                    </div>
                                </div>

                                <!-- Specific Fields -->
                                <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
                                    <h4 class="text-sm font-semibold text-gray-800 mb-4 border-b border-gray-100 pb-2">Specifications</h4>
                                    
                                    <div v-if="formData.booking_type === 'Flight'" class="grid grid-cols-2 gap-4">
                                        <div><label class="block text-xs text-gray-500 mb-1">Airline</label><autocomplete-input field="airline" v-model="formData.airline" inputClass="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Flight No.</label><input type="text" v-model="formData.flight_number" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Seat Class</label><input type="text" v-model="formData.seat_class" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">PNR Status</label><input type="text" v-model="formData.pnr_status" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                    </div>
                                    <div v-else-if="formData.booking_type === 'Train'" class="grid grid-cols-2 gap-4">
                                        <div><label class="block text-xs text-gray-500 mb-1">Train No.</label><autocomplete-input field="train_number" v-model="formData.train_number" inputClass="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Class</label><input type="text" v-model="formData.seat_class" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Coach/Seat</label><input type="text" v-model="formData.coach_number" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Platform</label><input type="text" v-model="formData.platform" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div class="col-span-2"><label class="block text-xs text-gray-500 mb-1">PNR</label><input type="text" v-model="formData.pnr_status" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                    </div>
                                    <div v-else-if="formData.booking_type === 'Bus'" class="grid grid-cols-2 gap-4">
                                        <div><label class="block text-xs text-gray-500 mb-1">Operator</label><autocomplete-input field="bus_operator" v-model="formData.bus_operator" inputClass="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Bus PNR</label><input type="text" v-model="formData.bus_pnr" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Pickup</label><input type="text" v-model="formData.pickup_point" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Drop</label><input type="text" v-model="formData.drop_point" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                    </div>
                                    <div v-else-if="formData.booking_type === 'Hotel'" class="grid grid-cols-2 gap-4">
                                        <div><label class="block text-xs text-gray-500 mb-1">Hotel Name</label><autocomplete-input field="hotel_name" v-model="formData.hotel_name" inputClass="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" /></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Room Type</label><input type="text" v-model="formData.room_type" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div class="col-span-2"><label class="block text-xs text-gray-500 mb-1">Address</label><input type="text" v-model="formData.hotel_address" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Check-in</label><input type="text" v-model="formData.check_in_time" placeholder="12:00 PM" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                        <div><label class="block text-xs text-gray-500 mb-1">Check-out</label><input type="text" v-model="formData.check_out_time" placeholder="11:00 AM" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"></div>
                                    </div>
                                </div>

                                <!-- Passengers -->
                                <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
                                    <div class="flex justify-between items-center mb-4 border-b border-gray-100 pb-2">
                                        <h4 class="text-sm font-semibold text-gray-800">Passengers</h4>
                                        <button type="button" @click="addPassenger" class="text-xs font-semibold text-brand-600 bg-brand-50 px-2 py-1 rounded">
                                            + Add
                                        </button>
                                    </div>
                                    <div class="space-y-4">
                                         <div v-for="(pax, idx) in formData.employees" :key="idx" class="p-4 bg-gray-50 rounded-xl relative group passenger-card">
                                            <div class="grid grid-cols-2 gap-3 mb-3">
                                                <div>
                                                    <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">Name</label>
                                                    <autocomplete-input field="employee_name" v-model="pax.name" @select="(s) => autofillPassenger(pax,'name',s)" inputClass="w-full px-3 py-1.5 border border-gray-200 rounded text-sm"/>
                                                </div>
                                                <div>
                                                    <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">Phone</label>
                                                    <autocomplete-input field="employee_phone" v-model="pax.phone" @select="(s) => autofillPassenger(pax,'phone',s)" inputClass="w-full px-3 py-1.5 border border-gray-200 rounded text-sm" />
                                                </div>
                                            </div>
                                            <div class="grid grid-cols-3 gap-3">
                                                <div>
                                                    <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">Designation</label>
                                                    <input type="text" v-model="pax.designation" class="w-full px-3 py-1.5 border border-gray-200 rounded text-sm">
                                                </div>
                                                <div>
                                                    <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">ID Type</label>
                                                    <select v-model="pax.id_type" class="w-full px-3 py-1.5 border border-gray-200 rounded text-sm">
                                                        <option value="">None</option>
                                                        <option value="Aadhaar">Aadhaar</option>
                                                        <option value="PAN">PAN</option>
                                                        <option value="Passport">Passport</option>
                                                        <option value="Voter ID">Voter ID</option>
                                                        <option value="DL">DL</option>
                                                    </select>
                                                </div>
                                                <div>
                                                    <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1">ID No.</label>
                                                    <input type="text" v-model="pax.id_number" class="w-full px-3 py-1.5 border border-gray-200 rounded text-sm">
                                                </div>
                                            </div>
                                            <button v-if="formData.employees.length > 1" type="button" @click="removePassenger(idx)" class="absolute -right-2 -top-2 bg-white text-gray-400 hover:text-red-500 rounded-full border shadow-sm p-1">
                                                <i class='bx bx-x'></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Right Column -->
                            <div class="md:col-span-4 space-y-6">
                                <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
                                    <h4 class="text-sm font-semibold text-gray-800 mb-4 border-b border-gray-100 pb-2">Status & Cost</h4>
                                    <div class="space-y-4">
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">Status</label>
                                            <select v-model="formData.status" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white font-medium">
                                                <option v-for="s in ['Pending', 'Confirmed', 'Completed', 'Cancelled']" :key="s" :value="s">{{ s }}</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">Cost (₹)</label>
                                            <input type="number" v-model="formData.cost" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-bold">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1.5">Internal Notes</label>
                                            <textarea v-model="formData.notes" rows="6" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none"></textarea>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            
            <div v-else class="flex flex-col justify-center items-center h-64 text-red-500">
                <i class='bx bx-error-circle text-4xl mb-2'></i>
                <span class="text-sm font-medium">Failed to load booking. It may have been deleted.</span>
            </div>
        </div>
    `,
    setup() {
        const route = VueRouter.useRoute();
        const router = VueRouter.useRouter();
        const booking = ref(null);
        const loading = ref(true);
        const isEditing = ref(false);
        const saving = ref(false);
        const documents = ref([]);
        const uploadingDoc = ref(false);

        const formData = reactive({
            booking_id: '',
            booking_type: 'Flight',
            booking_date: '',
            from_city: '',
            to_city: '',
            start_datetime: '',
            end_datetime: '',
            status: 'Pending',
            cost: 0,
            notes: '',
            employees: [],
            airline: '', flight_number: '', pnr_status: '', seat_class: '',
            train_number: '', coach_number: '', platform: '',
            bus_operator: '', bus_pnr: '', pickup_point: '', drop_point: '',
            hotel_name: '', room_type: '', hotel_address: '',
            check_in_time: '', check_out_time: ''
        });

        let mapInstance = null;

        const initMap = async () => {
            if (!booking.value || booking.value.booking_type === 'Hotel' || !booking.value.from_city || !booking.value.to_city) return;

            await new Promise(r => setTimeout(r, 150));
            const container = document.getElementById('routeMap');
            if (!container) return;

            if (mapInstance && mapInstance.remove) { mapInstance.remove(); }
            mapInstance = L.map('routeMap', { zoomControl: false }).setView([20.5937, 78.9629], 5);

            const isDark = document.documentElement.classList.contains('dark');
            const tileTheme = isDark ? 'dark_all' : 'light_all';

            L.tileLayer(`https://{s}.basemaps.cartocdn.com/${tileTheme}/{z}/{x}/{y}{r}.png`, {
                attribution: '&copy; CartoDB',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(mapInstance);

            try {
                const [fromRes, toRes] = await Promise.all([
                    fetch(`/api/v1/search/geocode?q=${encodeURIComponent(booking.value.from_city)}`).then(r => r.json()),
                    fetch(`/api/v1/search/geocode?q=${encodeURIComponent(booking.value.to_city)}`).then(r => r.json())
                ]);

                if (fromRes.length > 0 && toRes.length > 0) {
                    const fromCoords = [parseFloat(fromRes[0].lat), parseFloat(fromRes[0].lon)];
                    const toCoords = [parseFloat(toRes[0].lat), parseFloat(toRes[0].lon)];

                    let color = '#0ea5e9';
                    if (booking.value.booking_type === 'Train') color = '#22c55e';
                    if (booking.value.booking_type === 'Bus') color = '#f97316';

                    L.circleMarker(fromCoords, { radius: 6, color, fillOpacity: 1, stroke: true, weight: 2 }).addTo(mapInstance).bindPopup(booking.value.from_city);
                    L.circleMarker(toCoords, { radius: 6, color: '#f43f5e', fillOpacity: 1, stroke: true, weight: 2 }).addTo(mapInstance).bindPopup(booking.value.to_city);

                    const placeTransitIcon = (points, type, routeColor) => {
                        if (points.length < 2) return;
                        const midIdx = Math.floor(points.length / 2);
                        let html = '';
                        if (type === 'Flight') {
                            const p1 = points[Math.max(0, midIdx - 1)];
                            const p2 = points[Math.min(points.length - 1, midIdx + 1)];
                            const dy = p2[0] - p1[0];
                            const dx = p2[1] - p1[1];
                            const angle = Math.atan2(-dy, dx) * 180 / Math.PI;
                            html = `<div style="transform: rotate(${angle + 45}deg); color: ${routeColor};" class="text-3xl marker-glow drop-shadow-md">
                                        <i class='bx bxs-plane-alt'></i>
                                    </div>`;
                        } else {
                            const iconClass = type === 'Train' ? 'bxs-train' : 'bxs-bus';
                            html = `<div style="color: ${routeColor};" class="marker-glow bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-lg border-2 border-current">
                                        <i class='bx ${iconClass} text-lg'></i>
                                    </div>`;
                        }
                        L.marker(points[midIdx], {
                            icon: L.divIcon({ html, className: 'bg-transparent border-0', iconAnchor: type === 'Flight' ? [14, 14] : [16, 16] })
                        }).addTo(mapInstance);
                    };

                    const drawRoute = (points, isFlight) => {
                        const dash = isFlight ? '8, 12' : '15, 10';
                        const className = isFlight ? 'path-flow-flight' : 'path-flow-ground';
                        const routeLine = L.polyline(points, { color, weight: isFlight ? 3 : 4, opacity: 0.8, dashArray: dash, className }).addTo(mapInstance);
                        placeTransitIcon(points, booking.value.booking_type, color);
                        mapInstance.fitBounds(routeLine.getBounds(), { padding: [40, 40] });
                    };

                    if (booking.value.booking_type === 'Flight') {
                        try {
                            const generator = new arc.GreatCircle({ x: fromCoords[1], y: fromCoords[0] }, { x: toCoords[1], y: toCoords[0] });
                            const line = generator.Arc(100, { offset: 10 });
                            const curvePoints = line.geometries[0].coords.map(c => [c[1], c[0]]);
                            drawRoute(curvePoints, true);
                        } catch (e) {
                            console.warn("Arc failed", e);
                            drawRoute([fromCoords, toCoords], true);
                        }
                    } else {
                        try {
                            const res = await fetch(`https://router.project-osrm.org/route/v1/driving/${fromCoords[1]},${fromCoords[0]};${toCoords[1]},${toCoords[0]}?overview=simplified&geometries=geojson`);
                            const data = await res.json();
                            if (data && data.code === 'Ok' && data.routes && data.routes.length > 0) {
                                const latLngs = data.routes[0].geometry.coordinates.map(c => [c[1], c[0]]);
                                drawRoute(latLngs, false);
                            } else {
                                drawRoute([fromCoords, toCoords], false);
                            }
                        } catch (e) {
                            console.warn("OSRM routing proxy failed:", e);
                            drawRoute([fromCoords, toCoords], false);
                        }
                    }
                }
            } catch (e) { console.error('Map loading failed', e); }
        };

        const fetchData = async () => {
            // Add custom map animations if missing
            if (!document.getElementById('tracker-custom-css')) {
                const style = document.createElement('style');
                style.id = 'tracker-custom-css';
                style.innerHTML = `
                    .path-flow-flight { animation: flowDashFlight 30s linear infinite; }
                    .path-flow-ground { animation: flowDashGround 40s linear infinite; }
                    @keyframes flowDashFlight { to { stroke-dashoffset: -200; } }
                    @keyframes flowDashGround { to { stroke-dashoffset: -200; } }
                    .marker-glow { filter: drop-shadow(0 0 6px currentColor); }
                `;
                document.head.appendChild(style);
            }

            loading.value = true;
            try {
                let url = `/api/bookings/${route.params.id}`;
                booking.value = await api.request(url);
                fetchDocuments();
                if (!isEditing.value) initMap();
            } catch (error) {
                appState.showToast('Failed to load booking data', 'error');
            } finally {
                loading.value = false;
            }
        };

        const openEdit = () => {
            const b = { ...booking.value };
            for (let key in b) {
                if (b[key] === null) b[key] = '';
            }
            Object.assign(formData, {
                ...b,
                booking_date: b.booking_date ? b.booking_date.substring(0, 16) : '',
                start_datetime: b.start_datetime ? b.start_datetime.substring(0, 16) : '',
                end_datetime: b.end_datetime ? b.end_datetime.substring(0, 16) : '',
                employees: b.employees.map(e => ({
                    name: e.name, phone: e.phone,
                    email: e.email || '',
                    company_name: e.company_name || '',
                    designation: e.designation || '',
                    id_type: e.id_type || '',
                    id_number: e.id_number || ''
                }))
            });
            isEditing.value = true;
        };

        const saveEdit = async () => {
            if (!formData.from_city || !formData.start_datetime || !formData.end_datetime) {
                return appState.showToast('Please fill required fields', 'error');
            }
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

                await api.request(`/api/bookings/${booking.value.booking_id}`, {
                    method: 'PUT',
                    body: payload
                });
                appState.showToast('Booking updated successfully');
                isEditing.value = false;
                await fetchData();
            } catch (e) {
                console.error(e);
            } finally {
                saving.value = false;
            }
        };

        const toggleStatus = async (bk) => {
            const cycle = { 'Pending': 'Confirmed', 'Confirmed': 'Completed', 'Completed': 'Cancelled', 'Cancelled': 'Pending' };
            const nextStatus = cycle[bk.status] || 'Pending';
            try {
                const res = await api.request(`/api/bookings/${bk.booking_id}/status`, {
                    method: 'PATCH',
                    body: { status: nextStatus }
                });
                bk.status = res.status;
                appState.showToast('Status updated');
            } catch (e) { }
        };

        const updateStatus = async (newStatus) => {
            if (!confirm(`Change status to ${newStatus}?`)) return;
            try {
                await api.request(`/api/bookings/${booking.value.booking_id}/status`, { method: 'PATCH', body: { status: newStatus } });
                appState.showToast('Status updated');
                fetchData();
            } catch (e) { console.error(e); }
        };

        const fetchDocuments = async () => {
            try {
                // Documents are under /api/documents, not /api/bookings/.../documents
                const res = await api.request(`/api/documents/${route.params.id}`);
                documents.value = res;
            } catch (err) { }
        };

        const downloadDoc = async (doc) => {
            try {
                const blob = await api.request(doc.url, { responseType: 'blob' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = doc.filename;
                a.click();
                setTimeout(() => window.URL.revokeObjectURL(url), 100);
            } catch (err) {
                appState.showToast('Failed to download document', 'error');
            }
        };

        const uploadDocument = async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            const docFormData = new FormData();
            docFormData.append('file', file);

            uploadingDoc.value = true;
            try {
                const res = await api.request(`/api/documents/${route.params.id}`, {
                    method: 'POST',
                    body: docFormData
                });
                // api.request throws on non-ok response, so if we reach here, it succeeded
                appState.showToast('Document uploaded successfully.', 'success');
                await fetchDocuments();
            } catch (e) {
                appState.showToast('Upload error', 'error');
            } finally {
                uploadingDoc.value = false;
                event.target.value = ''; // reset
            }
        };

        const deleteBooking = async () => {
            if (confirm('Delete this booking permanentlly?')) {
                try {
                    await api.request(`/api/bookings/${booking.value.booking_id}`, { method: 'DELETE' });
                    appState.showToast('Booking deleted');
                    router.push('/bookings');
                } catch (e) { }
            }
        };

        const addPassenger = () => formData.employees.push({ name: '', phone: '', email: '', company_name: '', designation: '', id_type: '', id_number: '' });
        const removePassenger = (idx) => formData.employees.splice(idx, 1);
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
                    appState.showToast(`Autofilled ${emp.name}`);
                }
            } catch (e) { }
        };

        const getTypeIcon = (type) => ({
            'Flight': 'bx-planet text-brand-500',
            'Train': 'bx-train text-emerald-500',
            'Bus': 'bx-bus text-orange-500',
            'Hotel': 'bx-building-house text-purple-500'
        }[type] || 'bx-bookmark');

        const formatDateTime = (isoStr) => {
            if (!isoStr) return 'N/A';
            const d = new Date(isoStr);
            return d.toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
        };

        const getStatusBadgeClass = (status) => {
            if (status === 'Confirmed') return 'inline-flex items-center justify-center bg-emerald-50 text-emerald-700 border border-emerald-200/60 px-3.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all shadow-sm';
            if (status === 'Completed') return 'inline-flex items-center justify-center bg-indigo-50 text-indigo-700 border border-indigo-200/60 px-3.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all shadow-sm';
            if (status === 'Pending') return 'inline-flex items-center justify-center bg-amber-50 text-amber-700 border border-amber-200/60 px-3.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all shadow-sm';
            return 'inline-flex items-center justify-center bg-red-50 text-red-700 border border-red-200/60 px-3.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all shadow-sm';
        };

        onMounted(() => fetchData());
        watch(() => route.params.id, (id) => { if (id && route.name === 'bookingDetail') fetchData(); });

        return {
            booking, loading, isEditing, saving, formData,
            toggleStatus, deleteBooking, openEdit, saveEdit,
            addPassenger, removePassenger, autofillPassenger, getTypeIcon,
            formatDateTime, getStatusBadgeClass,
            updateStatus, documents, uploadingDoc, uploadDocument
        };
    }
});
