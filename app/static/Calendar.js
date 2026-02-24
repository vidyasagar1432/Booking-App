const CalendarView = defineComponent({
    template: `
        <div class="space-y-6 max-w-6xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
            <div class="flex items-center justify-between premium-card px-6 py-5 rounded-3xl shrink-0 border border-gray-100 dark:border-gray-700 shadow-sm relative overflow-hidden">
                <div class="absolute inset-y-0 left-0 w-2 bg-brand-500 rounded-l-3xl"></div>
                <div>
                    <h2 class="text-2xl font-black text-gray-900 leading-tight">Scheduling Matrix</h2>
                    <p class="text-xs text-gray-500 font-medium tracking-wide">Visualize active deployments and logistics spanning real-time dates.</p>
                </div>
                <div class="flex flex-wrap items-center gap-3">
                    <div class="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 p-1 rounded-xl border border-gray-100 dark:border-gray-700">
                        <select v-model="filters.type" class="bg-transparent border-none text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 py-1.5 px-3 focus:ring-0 cursor-pointer hover:bg-white dark:hover:bg-gray-700 rounded-lg transition-colors">
                            <option value="">All Types</option>
                            <option value="Flight">Flight</option>
                            <option value="Train">Train</option>
                            <option value="Bus">Bus</option>
                            <option value="Hotel">Hotel</option>
                        </select>
                        <span class="w-px h-4 bg-gray-200 dark:bg-gray-700 mx-1"></span>
                        <select v-model="filters.status" class="bg-transparent border-none text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 py-1.5 px-3 focus:ring-0 cursor-pointer hover:bg-white dark:hover:bg-gray-700 rounded-lg transition-colors">
                            <option value="">All Statuses</option>
                            <option value="Confirmed">Confirmed</option>
                            <option value="Pending">Pending</option>
                            <option value="Completed">Completed</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                    </div>

                    <div class="flex items-center gap-3 bg-white dark:bg-gray-800 p-1.5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
                        <button @click="prevMonth" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-400 hover:text-brand-600 transition-colors">
                            <i class='bx bx-chevron-left text-xl'></i>
                        </button>
                        <span class="text-sm font-bold text-gray-700 dark:text-gray-200 uppercase tracking-widest px-4 min-w-[140px] text-center">
                            {{ monthName }} {{ year }}
                        </span>
                        <button @click="nextMonth" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-400 hover:text-brand-600 transition-colors">
                            <i class='bx bx-chevron-right text-xl'></i>
                        </button>
                    </div>
                </div>
            </div>

            <div class="flex-1 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm overflow-hidden flex flex-col">
                <!-- Days Header -->
                <div class="grid grid-cols-7 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50 shrink-0">
                    <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" 
                         class="py-3 text-[10px] font-black uppercase tracking-widest text-center text-gray-400 border-r border-gray-100 dark:border-gray-800 last:border-0">
                        {{ day }}
                    </div>
                </div>

                <!-- Calendar Grid -->
                <div class="grid grid-cols-7 flex-1 auto-rows-fr">
                    <div v-for="(cell, i) in calendarCells" :key="i"
                         :class="['p-2 border-r border-b border-gray-100 dark:border-gray-800 relative transition-colors flex flex-col overflow-visible', 
                                  !cell.isCurrentMonth ? 'bg-gray-50/50 dark:bg-gray-800/20 opacity-50' : 'hover:bg-brand-50/30 dark:hover:bg-brand-900/10 cursor-pointer group/cell']"
                         @click="cell.isCurrentMonth && selectDate(cell.date)">
                        
                        <div :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mb-1 shrink-0', 
                                     isToday(cell.date) ? 'bg-brand-500 text-white shadow-md' : 'text-gray-600 dark:text-gray-300 group-hover/cell:text-brand-600']">
                            {{ cell.dayNum }}
                        </div>
                        
                        <!-- Events / Bookings -->
                        <div class="flex-1 overflow-visible space-y-1 mb-1">
                            <div v-for="evt in cell.events" :key="evt.booking_id" 
                                 @click.stop="$router.push('/bookings/' + evt.booking_id)"
                                 class="relative group/event px-2 py-1 bg-brand-50 dark:bg-brand-900/30 border border-brand-200/50 dark:border-brand-700/50 text-brand-700 dark:text-brand-300 text-[10px] font-bold rounded shadow-sm hover:shadow flex items-center gap-1 transition-all z-10 hover:z-50">
                                <i :class="getTypeIcon(evt.booking_type)"></i> 
                                <span class="truncate block w-full">{{ evt.booking_type !== 'Hotel' ? evt.to_city : evt.hotel_name || 'Hotel' }}</span>
                                
                                <!-- Hover Card -->
                                <div :class="['absolute w-64 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-4 opacity-0 invisible group-hover/event:opacity-100 group-hover/event:visible transition-all duration-200 pointer-events-none transform text-left z-[200]',
                                    (i < 14) ? 'top-[130%] mt-1 -translate-y-2 group-hover/event:translate-y-0' : 'bottom-[130%] mb-1 translate-y-2 group-hover/event:translate-y-0',
                                    (i % 7 === 0) ? '-left-2' : ((i % 7 === 6) ? '-right-2' : 'left-1/2 -translate-x-1/2')
                                ]">
                                    <div class="flex items-center gap-2 mb-2 border-b border-gray-100 dark:border-gray-700 pb-2">
                                        <div class="w-8 h-8 rounded-full bg-brand-50 dark:bg-brand-900/50 text-brand-600 flex items-center justify-center shrink-0">
                                            <i class="text-lg" :class="getTypeIcon(evt.booking_type)"></i>
                                        </div>
                                        <div class="min-w-0">
                                            <div class="text-xs font-black text-gray-900 dark:text-gray-100 truncate">{{ evt.booking_id }}</div>
                                            <div class="text-[10px] text-gray-500 uppercase font-bold tracking-wider">{{ evt.status }}</div>
                                        </div>
                                    </div>
                                    <div class="space-y-1.5 text-xs text-gray-600 dark:text-gray-300">
                                        <div class="flex items-start gap-2" v-if="evt.booking_type !== 'Hotel'">
                                            <i class='bx bx-trip mt-0.5 opacity-60'></i>
                                            <span class="truncate break-all">{{ evt.from_city || 'Unknown' }} &rarr; {{ evt.to_city || 'Unknown' }}</span>
                                        </div>
                                        <div class="flex items-start gap-2" v-if="evt.booking_type === 'Hotel'">
                                            <i class='bx bxs-building-house mt-0.5 opacity-60'></i>
                                            <span class="truncate">{{ evt.hotel_name || 'Hotel' }}</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <i class='bx bx-time-five opacity-60'></i>
                                            <span>{{ new Date(evt.start_datetime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <i class='bx bx-money opacity-60'></i>
                                            <span class="font-bold text-gray-800 dark:text-gray-200">₹{{ evt.cost.toLocaleString() }}</span>
                                        </div>
                                    </div>
                                    <div v-if="evt.employees && evt.employees.length > 0" class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 space-y-2">
                                        <div v-for="(emp, idx) in evt.employees.slice(0, 3)" :key="emp.id" class="flex items-center gap-2">
                                            <div class="w-5 h-5 rounded-full bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 flex items-center justify-center text-[10px] font-bold shrink-0">
                                                {{ emp.name.charAt(0).toUpperCase() }}
                                            </div>
                                            <div class="min-w-0 flex-1">
                                                <div class="text-[10px] font-bold text-gray-800 dark:text-gray-200 truncate leading-none">{{ emp.name }}</div>
                                                <div class="text-[9px] text-gray-500 truncate mt-0.5">{{ emp.company_name || 'Independent' }}</div>
                                            </div>
                                        </div>
                                        <div v-if="evt.employees.length > 3" class="text-[9px] font-bold text-brand-600 text-center uppercase tracking-widest pt-1">
                                            + {{ evt.employees.length - 3 }} More Passenger{{ evt.employees.length - 3 > 1 ? 's' : '' }}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
        </div>
    `,
    setup() {
        const currentDate = ref(new Date());
        const bookings = ref([]);
        const filters = reactive({
            type: '',
            status: ''
        });

        const fetchBookings = async () => {
            try {
                const start = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1).toISOString();
                const end = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 0).toISOString();

                let url = `/api/bookings?page=1&size=500&date_from=${start}&date_to=${end}`;
                if (filters.type) url += `&type=${filters.type}`;
                if (filters.status) url += `&status=${filters.status}`;

                const res = await api.request(url);
                if (res.items) bookings.value = res.items;
                else bookings.value = []; // empty out if no results mapped
            } catch (e) {
                console.error("Calendar fetch error:", e);
                bookings.value = [];
            }
        };

        watch(filters, fetchBookings);

        const getTypeIcon = (type) => {
            if (type === 'Flight') return 'bx bxs-plane-alt';
            if (type === 'Train') return 'bx bxs-train';
            if (type === 'Bus') return 'bx bxs-bus';
            return 'bx bxs-building-house';
        };

        const isToday = (date) => {
            const today = new Date();
            return date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();
        };

        const monthName = computed(() => currentDate.value.toLocaleString('default', { month: 'long' }));
        const year = computed(() => currentDate.value.getFullYear());

        const prevMonth = () => {
            currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() - 1));
            fetchBookings();
        };

        const nextMonth = () => {
            currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + 1));
            fetchBookings();
        };

        const calendarCells = computed(() => {
            const y = currentDate.value.getFullYear();
            const m = currentDate.value.getMonth();
            const firstDay = new Date(y, m, 1);
            const lastDay = new Date(y, m + 1, 0);

            const startDate = new Date(firstDay);
            startDate.setDate(startDate.getDate() - startDate.getDay()); // backtrack to Sunday

            const endDate = new Date(lastDay);
            if (endDate.getDay() !== 6) {
                endDate.setDate(endDate.getDate() + (6 - endDate.getDay())); // push forward to Saturday
            }

            const cells = [];
            const cur = new Date(startDate);
            while (cur <= endDate) {
                const cellDate = new Date(cur);
                const events = bookings.value.filter(b => {
                    const bDate = new Date(b.start_datetime);
                    return bDate.getDate() === cellDate.getDate() && bDate.getMonth() === cellDate.getMonth() && bDate.getFullYear() === cellDate.getFullYear();
                });

                cells.push({
                    date: cellDate,
                    dayNum: cellDate.getDate(),
                    isCurrentMonth: cellDate.getMonth() === m,
                    events
                });
                cur.setDate(cur.getDate() + 1);
            }
            return cells;
        });

        const selectDate = (date) => {
            // Optional: click empty tile to create Booking on that date
            // appState.showToast('Selected date: ' + date.toLocaleDateString(), 'info');
        };

        onMounted(() => {
            fetchBookings();
        });

        return {
            monthName, year, prevMonth, nextMonth, calendarCells,
            isToday, getTypeIcon, selectDate, filters
        };
    }
});
