const DashboardView = defineComponent({
    template: `
        <div class="space-y-6">
            <!-- Advanced Header -->
            <div class="flex flex-col lg:flex-row justify-between lg:items-end gap-4 animate-fade-in">
                <div>
                    <h2 class="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2">
                         Executive Overview
                    </h2>
                    <p class="text-sm text-gray-500 font-medium">Real-time business intelligence and performance tracking</p>
                </div>
                
                <div class="flex flex-wrap items-center gap-2 bg-white p-1.5 rounded-2xl shadow-sm border border-gray-100">
                    <div class="flex items-center px-3 border-r border-gray-100">
                        <i class='bx bx-filter-alt text-brand-500 mr-2'></i>
                        <select v-model="filters.type" @change="fetchData" class="bg-transparent border-none text-xs font-bold uppercase tracking-wider text-gray-600 focus:ring-0 cursor-pointer">
                            <option value="">All Streams</option>
                            <option value="Flight">Flights</option>
                            <option value="Train">Trains</option>
                            <option value="Bus">Buses</option>
                            <option value="Hotel">Hotels</option>
                        </select>
                    </div>
                    <div class="flex items-center px-2">
                        <input type="date" v-model="filters.date_from" @change="fetchData" class="bg-transparent border-none focus:ring-0 text-[11px] font-bold text-gray-500 w-28">
                        <span class="text-gray-300 mx-1">—</span>
                        <input type="date" v-model="filters.date_to" @change="fetchData" class="bg-transparent border-none focus:ring-0 text-[11px] font-bold text-gray-500 w-28">
                    </div>
                    <button @click="fetchData" class="p-2 bg-brand-50 text-brand-600 rounded-xl hover:bg-brand-100 transition-colors">
                        <i class='bx bx-refresh text-lg' :class="{'bx-spin': loading}"></i>
                    </button>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="flex flex-col justify-center items-center h-96 text-brand-600 animate-pulse">
                <i class='bx bx-loader-alt bx-spin text-5xl mb-4'></i>
                <span class="text-sm font-bold tracking-widest uppercase opacity-60">Synthesizing Analytics...</span>
            </div>
            
            <div v-else class="space-y-8">
                <!-- Advanced KPIs -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div v-for="kpi in kpiCards" :key="kpi.label" class="premium-card group hover:shadow-xl hover:shadow-brand-500/5 transition-all duration-500 rounded-3xl p-6 relative overflow-hidden">
                        <div :class="['absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-10 group-hover:scale-150 transition-transform duration-700', kpi.colorClass]"></div>
                        <div class="flex items-start justify-between relative z-10">
                            <div :class="['p-2.5 rounded-2xl flex items-center justify-center shadow-lg shadow-black/5', kpi.bgClass]">
                                <i :class="['bx text-xl', kpi.icon, kpi.textClass]"></i>
                            </div>
                            <span v-if="kpi.trend" class="flex items-center gap-0.5 text-[10px] font-black text-emerald-500 bg-emerald-50 px-2 py-1 rounded-lg">
                                <i class='bx bx-up-arrow-alt'></i> {{ kpi.trend }}
                            </span>
                        </div>
                        <div class="mt-5 relative z-10">
                            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest">{{ kpi.label }}</h3>
                            <div class="flex items-baseline gap-1 mt-1">
                                <span v-if="kpi.isCurrency" class="text-lg font-bold text-gray-400">₹</span>
                                <span class="text-3xl font-black text-gray-900 tracking-tight">{{ kpi.value }}</span>
                            </div>
                            <p class="text-[10px] text-gray-500 mt-2 font-medium">{{ kpi.subtext }}</p>
                        </div>
                    </div>
                </div>

                <!-- Deep Insights Tabs -->
                <div class="flex items-center gap-1 justify-center bg-gray-100/50 p-1 rounded-2xl w-fit mx-auto border border-gray-200/50">
                    <button v-for="tab in tabOptions" :key="tab.id"
                            @click="setActiveTab(tab.id)"
                            :class="['px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all',
                                     activeTab === tab.id ? 'bg-white text-brand-600 shadow-sm' : 'text-gray-400 hover:text-gray-600']">
                        {{ tab.label }}
                    </button>
                </div>

                <!-- Primary Analysis Row -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- Revenue Analytics (Full Span on Revenue Tab, otherwise 2 cols) -->
                    <div :class="['premium-card p-6 rounded-3xl transition-all duration-500', activeTab === 'revenue' ? 'lg:col-span-3' : 'lg:col-span-2']" v-show="['all', 'revenue'].includes(activeTab)">
                        <div class="flex items-center justify-between mb-8">
                            <div>
                                <h3 class="text-lg font-black text-gray-800 tracking-tight">Financial Performance</h3>
                                <p class="text-xs text-gray-500 font-medium">Monthly revenue stream and transaction trends</p>
                            </div>
                            <div class="flex gap-2">
                                <span class="flex items-center gap-1.5 text-[10px] font-bold text-gray-400 border border-gray-100 rounded-lg px-2.5 py-1.5">
                                    <span class="w-1.5 h-1.5 rounded-full bg-brand-500"></span> Actual Revenue
                                </span>
                            </div>
                        </div>
                        <div id="revenueChart" class="h-80 w-full"></div>
                    </div>

                    <!-- Market Share (Distribution) -->
                    <div class="premium-card p-6 rounded-3xl" v-show="['all', 'market'].includes(activeTab)">
                        <div class="mb-8">
                            <h3 class="text-lg font-black text-gray-800 tracking-tight">Stream Distribution</h3>
                            <p class="text-xs text-gray-500 font-medium">Market share by booking modality</p>
                        </div>
                        <div id="typeChart" class="h-80 w-full"></div>
                    </div>
                </div>

                <!-- Detailed Breakdown Row -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8" v-show="activeTab !== 'financials'">
                    <!-- Category Specific Analytics (Flights/Hotels details) -->
                    <div class="premium-card p-8 rounded-3xl">
                        <div class="flex items-center justify-between mb-8">
                            <div>
                                <h3 class="text-lg font-black text-gray-800 tracking-tight">Category Intelligence</h3>
                                <p class="text-xs text-gray-500 font-medium">{{ breakdownSubtext }}</p>
                            </div>
                        </div>
                        <div id="categoryChart" class="h-80 w-full"></div>
                    </div>

                    <!-- Corporate Allocation -->
                    <div class="premium-card p-8 rounded-3xl">
                        <div class="flex items-center justify-between mb-8">
                            <div>
                                <h3 class="text-lg font-black text-gray-800 tracking-tight">Corporate Portfolio</h3>
                                <p class="text-xs text-gray-500 font-medium">Top value contributing organizations</p>
                            </div>
                        </div>
                        <div id="companiesChart" class="h-80 w-full"></div>
                    </div>
                </div>

                <!-- High Volume Entities Table -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8" v-show="activeTab === 'all' || activeTab === 'corporate'">
                    <!-- Top Employees List -->
                    <div class="lg:col-span-1 premium-card p-6 rounded-3xl">
                        <h3 class="text-sm font-black text-gray-800 uppercase tracking-widest mb-6">Top Value Agents</h3>
                        <div class="space-y-4">
                            <div v-for="(emp, index) in topEntities" :key="index" class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-2xl transition-colors group">
                                <div class="flex items-center gap-3">
                                    <div class="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center font-bold text-xs">
                                        {{ emp.label.charAt(0) }}
                                    </div>
                                    <div>
                                        <p class="text-sm font-bold text-gray-800 group-hover:text-brand-600 transition-colors">{{ emp.label }}</p>
                                        <p class="text-[10px] text-gray-500 font-bold uppercase tracking-tighter">Contributor</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm font-black text-gray-900">₹{{ emp.value.toLocaleString() }}</p>
                                    <div class="w-16 h-1 bg-gray-100 rounded-full mt-1.5 overflow-hidden">
                                        <div class="h-full bg-brand-500" :style="{ width: (emp.value / maxEntityValue * 100) + '%' }"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Daily Flux Chart -->
                    <div class="lg:col-span-2 premium-card p-6 rounded-3xl">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-sm font-black text-gray-800 uppercase tracking-widest">Network Throughput (14d)</h3>
                            <span class="text-[10px] font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg uppercase tracking-wider">Passenger Flux</span>
                        </div>
                        <div id="paxChart" class="h-80 w-full"></div>
                    </div>
                </div>
            </div>
        </div>
    `,
    setup() {
        const kpis = ref({});
        const chartsData = ref({});
        const loading = ref(true);
        const filters = reactive({ type: '', status: '', date_from: '', date_to: '' });
        const activeTab = ref('all');
        let chartInstances = {};

        const tabOptions = [
            { id: 'all', label: 'Overall' },
            { id: 'revenue', label: 'Revenue' },
            { id: 'market', label: 'Market' },
            { id: 'corporate', label: 'Corporate' },
            { id: 'inventory', label: 'Streams' }
        ];

        const kpiCards = computed(() => [
            { label: 'Total Enterprise Value', value: (kpis.value.total_revenue || 0).toLocaleString('en-IN'), icon: 'bx-diamond', bgClass: 'bg-emerald-500', textClass: 'text-white', colorClass: 'bg-emerald-400', isCurrency: true, trend: '12%', subtext: 'Gross transaction volume (GTV)' },
            { label: 'Network Throughput', value: (kpis.value.total_bookings || 0).toLocaleString(), icon: 'bx-radar', bgClass: 'bg-indigo-600', textClass: 'text-white', colorClass: 'bg-indigo-400', trend: '8%', subtext: 'Active operational volume' },
            { label: 'Client Portfolio', value: (kpis.value.total_companies || 0).toLocaleString(), icon: 'bx-buildings', bgClass: 'bg-orange-500', textClass: 'text-white', colorClass: 'bg-orange-400', trend: '5%', subtext: 'Corporate entities under mgt' },
            { label: 'Agent Database', value: (kpis.value.total_employees || 0).toLocaleString(), icon: 'bx-user-voice', bgClass: 'bg-brand-500', textClass: 'text-white', colorClass: 'bg-brand-400', trend: '2%', subtext: 'Registered travel coordinators' },
        ]);

        const breakdownSubtext = computed(() => {
            if (filters.type === 'Flight') return 'Airline operator distribution and share';
            if (filters.type === 'Hotel') return 'Property performance and volume';
            return 'Global logistics and transport breakdown';
        });

        const topEntities = computed(() => {
            const data = chartsData.value.top_employees || chartsData.value.top_companies || { labels: [], values: [] };
            return data.labels.slice(0, 6).map((label, i) => ({ label, value: data.values[i] }));
        });

        const maxEntityValue = computed(() => Math.max(...topEntities.value.map(e => e.value), 1));

        const setActiveTab = (tab) => {
            activeTab.value = tab;
            setTimeout(initCharts, 50);
        };

        const hasChartData = (key) => chartsData.value && chartsData.value[key] && chartsData.value[key].values?.length > 0;

        const initCharts = () => {
            if (!chartsData.value) return;
            Object.values(chartInstances).forEach(c => c.destroy());
            chartInstances = {};

            const commonOptions = {
                chart: { toolbar: { show: false }, fontFamily: 'Outfit, sans-serif' },
                dataLabels: { enabled: false },
                stroke: { curve: 'smooth', width: 3 },
                grid: { borderColor: '#f1f5f9', strokeDashArray: 4 }
            };

            // 1. Revenue
            if (hasChartData('monthly_revenue') && document.querySelector("#revenueChart")) {
                chartInstances.revenue = new ApexCharts(document.querySelector("#revenueChart"), {
                    ...commonOptions,
                    series: [{ name: 'Revenue (₹)', data: chartsData.value.monthly_revenue.values }],
                    chart: { ...commonOptions.chart, type: 'area', height: 320 },
                    xaxis: { categories: chartsData.value.monthly_revenue.labels, axisBorder: { show: false } },
                    colors: ['#0d9488'],
                    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.5, opacityTo: 0.02, stops: [0, 90, 100] } },
                    markers: { size: 5, colors: ['#fff'], strokeColors: '#0d9488', strokeWidth: 3 },
                    yaxis: { labels: { formatter: val => '₹' + (val / 1000).toFixed(0) + 'k' } }
                });
                chartInstances.revenue.render();
            }

            // 2. Types (Market)
            if (hasChartData('booking_types') && document.querySelector("#typeChart")) {
                chartInstances.type = new ApexCharts(document.querySelector("#typeChart"), {
                    ...commonOptions,
                    series: chartsData.value.booking_types.values,
                    labels: chartsData.value.booking_types.labels,
                    chart: { type: 'donut', height: 320 },
                    colors: ['#14b8a6', '#8b5cf6', '#f43f5e', '#f59e0b', '#3b82f6'],
                    plotOptions: { pie: { donut: { size: '75%', labels: { show: true, total: { show: true, label: 'TOTAL', fontSize: '12px', fontWeight: 800 } } } } },
                    stroke: { width: 0 }
                });
                chartInstances.type.render();
            }

            // 3. Category Intelligence
            let catData = chartsData.value.booking_types; // Default
            if (filters.type === 'Flight') catData = chartsData.value.airlines;
            if (filters.type === 'Hotel') catData = chartsData.value.hotels;
            if (filters.type === 'Train') catData = chartsData.value.trains;
            if (filters.type === 'Bus') catData = chartsData.value.buses;

            if (catData && document.querySelector("#categoryChart")) {
                chartInstances.category = new ApexCharts(document.querySelector("#categoryChart"), {
                    ...commonOptions,
                    series: [{ name: 'Count', data: catData.values }],
                    chart: { type: 'bar', height: 320 },
                    xaxis: { categories: catData.labels },
                    colors: ['#0d9488'],
                    plotOptions: { bar: { borderRadius: 8, columnWidth: '40%' } }
                });
                chartInstances.category.render();
            }

            // 4. Companies
            if (hasChartData('top_companies') && document.querySelector("#companiesChart")) {
                chartInstances.companies = new ApexCharts(document.querySelector("#companiesChart"), {
                    ...commonOptions,
                    series: [{ name: 'Contribution', data: chartsData.value.top_companies.values }],
                    chart: { type: 'bar', height: 320 },
                    xaxis: { categories: chartsData.value.top_companies.labels },
                    colors: ['#8b5cf6'],
                    plotOptions: { bar: { borderRadius: 8, horizontal: true, barHeight: '50%' } },
                    dataLabels: { enabled: true, style: { colors: ['#fff'], fontSize: '10px' } }
                });
                chartInstances.companies.render();
            }

            // 5. Pax Trend
            if (hasChartData('daily_passengers') && document.querySelector("#paxChart")) {
                chartInstances.pax = new ApexCharts(document.querySelector("#paxChart"), {
                    ...commonOptions,
                    series: [{ name: 'Passengers', data: chartsData.value.daily_passengers.values }],
                    chart: { type: 'line', height: 320 },
                    xaxis: { categories: chartsData.value.daily_passengers.labels },
                    colors: ['#3b82f6'],
                    stroke: { width: 4, dashArray: [0] },
                    markers: { size: 6, colors: ['#3b82f6'], strokeColors: '#fff', strokeWidth: 3 }
                });
                chartInstances.pax.render();
            }
        };

        const fetchData = async () => {
            loading.value = true;
            try {
                let url = '/api/analytics?detailed=true&';
                if (filters.type) url += `type=${filters.type}&`;
                if (filters.status) url += `status=${filters.status}&`;
                if (filters.date_from) url += `date_from=${filters.date_from}&`;
                if (filters.date_to) url += `date_to=${filters.date_to}&`;

                const data = await api.request(url);
                kpis.value = data.kpis;
                chartsData.value = data.charts;

                setTimeout(initCharts, 80);
            } catch (error) {
                appState.showToast('Failed to load dashboard intel', 'error');
            } finally {
                loading.value = false;
            }
        };

        onMounted(() => fetchData());

        return { kpis, loading, filters, fetchData, activeTab, setActiveTab, tabOptions, kpiCards, breakdownSubtext, topEntities, maxEntityValue };
    }
});
