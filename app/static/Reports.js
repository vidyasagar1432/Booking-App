const ReportsView = defineComponent({
    template: `
        <div class="space-y-6">
            <!-- Header & Period Filter -->
            <div class="premium-card p-4 rounded-2xl flex flex-col md:flex-row justify-between items-center gap-4">
                <div class="flex items-center gap-2">
                    <span class="w-1.5 h-6 bg-brand-500 rounded-full"></span>
                    <h2 class="text-xl font-bold text-gray-900">Detailed Analytics Reports</h2>
                </div>
                <div class="flex items-center gap-2 bg-gray-50 p-1.5 rounded-xl border border-gray-100/50">
                    <i class='bx bx-calendar text-gray-400 ml-2'></i>
                    <input type="date" v-model="filters.date_from" @change="fetchData" class="bg-transparent border-none focus:ring-0 text-sm font-medium text-gray-700 w-32">
                    <span class="text-gray-300 font-bold">/</span>
                    <input type="date" v-model="filters.date_to" @change="fetchData" class="bg-transparent border-none focus:ring-0 text-sm font-medium text-gray-700 w-32">
                </div>
            </div>

            <!-- Tab Navigation -->
            <div class="flex overflow-x-auto pb-4 gap-2 scrollbar-hide">
                <button v-for="tab in tabOptions" :key="tab.id"
                    @click="activeTab = tab.id"
                    :class="['px-6 py-2.5 rounded-xl text-sm font-bold transition-all whitespace-nowrap flex items-center gap-2 shadow-sm',
                             activeTab === tab.id ? 'bg-brand-600 text-white shadow-brand-500/20' : 'bg-white text-gray-500 hover:bg-gray-50 border border-gray-100']">
                    <i :class="['bx text-lg', tab.icon]"></i>
                    {{ tab.label }}
                </button>
            </div>

            <!-- Report Content -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <!-- Left Column: KPIs specific to context -->
                <div class="lg:col-span-1 space-y-6">
                    <div class="premium-card p-6 rounded-2xl">
                        <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-4">Metric Overview</h3>
                        <div class="space-y-4">
                            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100/50">
                                <span class="text-[10px] font-bold text-gray-400 uppercase">Total Revenue ({{ activeTabLabel }})</span>
                                <p class="text-2xl font-bold text-gray-900 mt-1">₹{{ kpis.total_revenue?.toLocaleString() || 0 }}</p>
                            </div>
                            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100/50">
                                <span class="text-[10px] font-bold text-gray-400 uppercase">Total Volume</span>
                                <p class="text-2xl font-bold text-gray-900 mt-1">{{ kpis.total_bookings?.toLocaleString() || 0 }} <span class="text-xs text-gray-400 font-medium ml-1">Orders</span></p>
                            </div>
                            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100/50">
                                <span class="text-[10px] font-bold text-gray-400 uppercase">Avg. Ticket Value</span>
                                <p class="text-2xl font-bold text-gray-900 mt-1">₹{{ kpis.avg_cost?.toLocaleString() || 0 }}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Additional Context Chart -->
                    <div class="premium-card p-6 rounded-2xl" v-if="hasChartData('statuses')">
                        <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-4">Status Distribution</h3>
                        <div id="statusChart" class="w-full"></div>
                    </div>
                </div>

                <!-- Right Column: Main Analysis Charts -->
                <div class="lg:col-span-2 space-y-6">
                    <!-- Trend Chart -->
                    <div class="premium-card p-6 rounded-2xl">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                                <i class='bx bx-trending-up text-brand-500'></i> Performance Trend
                            </h3>
                        </div>
                        <div id="trendChart" class="h-80"></div>
                    </div>

                    <!-- Breakdown Chart -->
                    <div class="premium-card p-6 rounded-2xl">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                                <i class='bx bx-stats text-brand-500'></i> Category Breakdown
                            </h3>
                        </div>
                        <div id="breakdownChart" class="h-80 flex items-center justify-center">
                            <div v-if="!currentBreakdownData" class="text-gray-400 italic text-sm">No specific breakdown data available for this selection.</div>
                            <div v-else id="breakdownChartElement" class="w-full h-full"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Global Leaderboard for Employees/Companies -->
            <div v-if="activeTab === 'all' || activeTab === 'employees' || activeTab === 'companies'" class="premium-card p-6 rounded-2xl animate-fade-in">
                 <div class="flex items-center justify-between mb-6">
                    <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                        <i class='bx bx-crown text-yellow-500'></i> Top Performance Rankings
                    </h3>
                </div>
                <div id="leaderboardChart" class="h-96"></div>
            </div>
        </div>
    `,
    setup() {
        const activeTab = ref('all');
        const filters = reactive({ date_from: '', date_to: '' });
        const kpis = ref({});
        const chartsData = ref({});
        const loading = ref(true);
        let chartInstances = {};

        const tabOptions = [
            { id: 'all', label: 'All Operations', icon: 'bx-grid-alt' },
            { id: 'Flight', label: 'Flights', icon: 'bx-paper-plane' },
            { id: 'Train', label: 'Trains', icon: 'bx-train' },
            { id: 'Bus', label: 'Buses', icon: 'bx-bus' },
            { id: 'Hotel', label: 'Hotels', icon: 'bx-hotel' },
            { id: 'employees', label: 'Employees', icon: 'bx-user' },
            { id: 'companies', label: 'Companies', icon: 'bx-buildings' },
        ];

        const activeTabLabel = computed(() => {
            return tabOptions.find(t => t.id === activeTab.value)?.label || 'Overview';
        });

        const currentBreakdownData = computed(() => {
            if (activeTab.value === 'Flight') return chartsData.value.airlines;
            if (activeTab.value === 'Hotel') return chartsData.value.hotels;
            if (activeTab.value === 'Train') return chartsData.value.trains;
            if (activeTab.value === 'Bus') return chartsData.value.buses;
            if (activeTab.value === 'all' || activeTab.value === 'employees' || activeTab.value === 'companies') return chartsData.value.top_companies;
            return null;
        });

        const hasChartData = (key) => {
            return chartsData.value && chartsData.value[key] && chartsData.value[key].values?.length > 0;
        };

        const initCharts = () => {
            // Cleanup
            Object.values(chartInstances).forEach(c => c.destroy());
            chartInstances = {};

            if (!chartsData.value) return;

            // 1. Trend Chart (Shared)
            if (hasChartData('monthly_revenue')) {
                chartInstances.trend = new ApexCharts(document.querySelector("#trendChart"), {
                    series: [{ name: 'Revenue', data: chartsData.value.monthly_revenue.values }],
                    chart: { type: 'area', height: 320, toolbar: { show: false }, fontFamily: 'Outfit, sans-serif' },
                    xaxis: { categories: chartsData.value.monthly_revenue.labels },
                    colors: ['#0d9488'],
                    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05 } },
                    stroke: { curve: 'smooth', width: 2 },
                    markers: { size: 4, colors: ['#fff'], strokeColors: '#0d9488', strokeWidth: 2 }
                });
                chartInstances.trend.render();
            }

            // 2. Status Chart (Pie)
            if (hasChartData('statuses')) {
                chartInstances.status = new ApexCharts(document.querySelector("#statusChart"), {
                    series: chartsData.value.statuses.values,
                    labels: chartsData.value.statuses.labels,
                    chart: { type: 'donut', height: 260, fontFamily: 'Outfit, sans-serif' },
                    colors: ['#14b8a6', '#f59e0b', '#ef4444', '#3b82f6'],
                    legend: { position: 'bottom' },
                    plotOptions: { pie: { donut: { size: '60%' } } }
                });
                chartInstances.status.render();
            }

            // 3. Breakdown Chart (Category specific)
            const breakdownData = currentBreakdownData.value;
            if (breakdownData && document.querySelector("#breakdownChartElement")) {
                chartInstances.breakdown = new ApexCharts(document.querySelector("#breakdownChartElement"), {
                    series: [{ name: 'Count', data: breakdownData.values }],
                    chart: { type: 'bar', height: 320, toolbar: { show: false }, fontFamily: 'Outfit, sans-serif' },
                    xaxis: { categories: breakdownData.labels },
                    colors: ['#8b5cf6'],
                    plotOptions: { bar: { borderRadius: 6, distributed: true } },
                    legend: { show: false }
                });
                chartInstances.breakdown.render();
            }

            // 4. Leaderboard Chart (Employees/Companies)
            if (activeTab.value === 'all' || activeTab.value === 'employees' || activeTab.value === 'companies') {
                const isEmp = activeTab.value === 'employees';
                const data = isEmp ? (chartsData.value.top_employees || chartsData.value.top_companies) : chartsData.value.top_companies;

                if (data && document.querySelector("#leaderboardChart")) {
                    chartInstances.leaderboard = new ApexCharts(document.querySelector("#leaderboardChart"), {
                        series: [{ name: 'Spend (₹)', data: data.values }],
                        chart: { type: 'bar', height: 380, toolbar: { show: false }, fontFamily: 'Outfit, sans-serif' },
                        xaxis: { categories: data.labels },
                        colors: [isEmp ? '#f43f5e' : '#3b82f6'],
                        plotOptions: {
                            bar: {
                                borderRadius: 8,
                                horizontal: true,
                                dataLabels: { position: 'top' }
                            }
                        },
                        dataLabels: {
                            enabled: true,
                            formatter: val => '₹' + val.toLocaleString(),
                            style: { colors: ['#64748b'] }
                        }
                    });
                    chartInstances.leaderboard.render();
                }
            }
        };

        const fetchData = async () => {
            loading.value = true;
            try {
                // Determine filter for API
                // If tab is a booking type, filter by it. If it's employees/companies, don't filter by type but ask for detailed.
                const isBookingType = ['Flight', 'Train', 'Bus', 'Hotel'].includes(activeTab.value);

                let url = `/api/analytics?detailed=true&`;
                if (isBookingType) url += `type=${activeTab.value}&`;
                if (filters.date_from) url += `date_from=${filters.date_from}&`;
                if (filters.date_to) url += `date_to=${filters.date_to}&`;

                const data = await api.request(url);
                kpis.value = data.kpis;
                chartsData.value = data.charts;

                setTimeout(initCharts, 50);
            } catch (error) {
                appState.showToast('Failed to fetch detailed analytics', 'error');
            } finally {
                loading.value = false;
            }
        };

        watch(activeTab, fetchData);

        onMounted(() => {
            fetchData();
        });

        return { activeTab, tabOptions, filters, kpis, loading, activeTabLabel, hasChartData, currentBreakdownData, fetchData };
    }
});
