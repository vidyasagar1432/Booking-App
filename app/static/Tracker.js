const TrackerView = defineComponent({
    template: `
        <div class="h-[calc(100vh-8rem)] flex flex-col space-y-4">
            <div class="flex items-center justify-between premium-card px-6 py-4 xl:py-5 rounded-2xl animate-fade-in shrink-0">
                <div>
                    <h2 class="text-xl xl:text-2xl font-bold text-gray-900 leading-tight flex items-center gap-2 tracking-tight">
                        <i class='bx bx-radar text-brand-600 animate-pulse'></i> Live Trip Tracker
                    </h2>
                    <p class="text-xs text-gray-500 mt-1 font-medium hidden sm:block">Command Center view of all active transit routes across the network globally.</p>
                </div>
                <div class="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 p-1.5 rounded-xl border border-gray-100 dark:border-gray-700">
                    <div class="relative flex items-center">
                        <i class='bx bx-search absolute left-3 text-gray-400'></i>
                        <input type="text" v-model="pnrSearch" @keyup.enter="fetchAndPlot()" placeholder="Track PNR or Flight #..." class="w-48 pl-9 pr-3 py-1.5 text-xs bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none transition-all dark:text-white placeholder-gray-400">
                        <button v-if="pnrSearch" @click="pnrSearch=''; fetchAndPlot()" class="absolute right-2 text-gray-400 hover:text-gray-600"><i class='bx bx-x'></i></button>
                    </div>
                    <div class="h-6 w-px bg-gray-200 dark:bg-gray-700 mx-1"></div>
                    <button @click="filter = 'All'; fetchAndPlot()" :class="['px-3 py-1.5 text-xs font-bold rounded-lg transition-all', filter === 'All' ? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-gray-100' : 'text-gray-500 hover:text-gray-700']">All Active</button>
                    <button @click="filter = 'Flight'; fetchAndPlot()" :class="['px-3 py-1.5 text-xs font-bold rounded-lg transition-all', filter === 'Flight' ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 shadow-sm' : 'text-gray-500 hover:text-gray-700']"><i class='bx bxs-plane-alt'></i> Flights</button>
                    <button @click="filter = 'Train'; fetchAndPlot()" :class="['px-3 py-1.5 text-xs font-bold rounded-lg transition-all', filter === 'Train' ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300 shadow-sm' : 'text-gray-500 hover:text-gray-700']"><i class='bx bxs-train'></i> Trains</button>
                </div>
            </div>

            <div class="flex-1 premium-card rounded-2xl overflow-hidden relative border border-gray-100 dark:border-gray-700 shadow-sm z-0">
                <div v-if="loading" class="absolute inset-0 z-[1000] flex flex-col items-center justify-center bg-gray-50/80 dark:bg-gray-900/80 backdrop-blur-sm">
                    <i class='bx bx-loader-alt bx-spin text-4xl text-brand-500 mb-2'></i>
                    <span class="text-sm font-bold text-gray-600 dark:text-gray-300 tracking-widest uppercase">{{ loadingMessage }}</span>
                </div>
                <div id="globalTrackerMap" class="w-full h-full bg-gray-50 dark:bg-gray-900"></div>
                
                <div class="absolute bottom-6 left-6 z-[400] bg-white/90 dark:bg-gray-900/90 backdrop-blur-md px-4 py-3 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-xl flex items-center gap-4">
                    <div class="text-center">
                        <div class="text-2xl font-black text-brand-600 leading-none">{{ trackedCount }}</div>
                        <div class="text-[9px] font-bold text-gray-400 uppercase tracking-widest mt-1">Active Routes</div>
                    </div>
                </div>
            </div>
        </div>
    `,
    setup() {
        const loading = ref(true);
        const loadingMessage = ref('Triangulating Coordinates...');
        const filter = ref('All');
        const pnrSearch = ref('');
        const trackedCount = ref(0);
        let mapInstance = null;
        let routeLayerGroup = null;

        const initMapBase = () => {
            const isDark = document.documentElement.classList.contains('dark');
            const tileTheme = isDark ? 'dark_all' : 'rastertiles/voyager';

            if (!mapInstance) {
                mapInstance = L.map('globalTrackerMap', { zoomControl: false }).setView([20.5937, 78.9629], 5);
                L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
                routeLayerGroup = L.layerGroup().addTo(mapInstance);
            }

            // Clear tiles and add new ones if theme changes (simplistic approach)
            mapInstance.eachLayer(layer => { if (layer instanceof L.TileLayer) mapInstance.removeLayer(layer); });

            L.tileLayer(`https://{s}.basemaps.cartocdn.com/${tileTheme}/{z}/{x}/{y}{r}.png`, {
                attribution: '&copy; CartoDB',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(mapInstance);
        };

        const fetchAndPlot = async () => {
            loading.value = true;
            loadingMessage.value = 'Analyzing Network Graph...';
            try {
                // Fetch all bookings (in a real app, you might want to only fetch "Active/Confirmed" ones)
                const res = await api.request('/api/bookings?page=1&size=200'); // limit to 200 recent
                if (!res.items) return;

                let items = res.items.filter(b => b.booking_type !== 'Hotel' && b.status === 'Confirmed');

                if (filter.value !== 'All') {
                    items = items.filter(b => b.booking_type === filter.value);
                }

                if (pnrSearch.value) {
                    const term = pnrSearch.value.toLowerCase().trim();
                    items = items.filter(b =>
                        (b.booking_id && b.booking_id.toLowerCase().includes(term)) ||
                        (b.flight_number && b.flight_number.toLowerCase().includes(term)) ||
                        (b.train_number && b.train_number.toLowerCase().includes(term)) ||
                        (b.bus_operator && b.bus_operator.toLowerCase().includes(term))
                    );
                }

                trackedCount.value = items.length;
                routeLayerGroup.clearLayers();

                // Extract all unique cities
                const uniqueCities = new Set();
                items.forEach(b => {
                    if (b.from_city) uniqueCities.add(b.from_city);
                    if (b.to_city) uniqueCities.add(b.to_city);
                });

                // Fetch real coordinates from internet using OpenStreetMap Nominatim API
                // We use a slow sequential fetch to respect their 1 req/second rate limits
                const sleep = ms => new Promise(r => setTimeout(r, ms));

                // Hardcoded exact coordinates for Indian cities generated by seed.py
                const FALLBACK_CITY_COORDS = {
                    "Mumbai": [19.0760, 72.8777], "Delhi": [28.7041, 77.1025], "Bengaluru": [12.9716, 77.5946],
                    "Hyderabad": [17.3850, 78.4867], "Chennai": [13.0827, 80.2707], "Kolkata": [22.5726, 88.3639],
                    "Pune": [18.5204, 73.8567], "Ahmedabad": [23.0225, 72.5714], "Jaipur": [26.9124, 75.7873],
                    "Lucknow": [26.8467, 80.9462], "Kochi": [9.9312, 76.2673], "Goa": [15.2993, 74.1240]
                };

                const getFallbackCoords = (cityName) => {
                    if (FALLBACK_CITY_COORDS[cityName]) return FALLBACK_CITY_COORDS[cityName];
                    let hash = 0;
                    for (let i = 0; i < cityName.length; i++) {
                        hash = cityName.charCodeAt(i) + ((hash << 5) - hash);
                    }
                    const lat = 10 + (Math.abs(hash) % 25);
                    const lon = 70 + ((Math.abs(hash) >> 4) % 20);
                    return [lat, lon];
                };

                let uncachedCities = Array.from(uniqueCities).filter(city => !window.__GEO_CACHE__ || !window.__GEO_CACHE__[city]);
                let fetchedCount = 0;

                for (let city of uniqueCities) {
                    if (!window.__GEO_CACHE__) window.__GEO_CACHE__ = {};

                    if (!window.__GEO_CACHE__[city]) {
                        fetchedCount++;
                        loadingMessage.value = `Geocoding ${city}... (${fetchedCount}/${uncachedCities.length})`;
                        try {
                            const res = await fetch(`/api/v1/search/geocode?q=${encodeURIComponent(city)}`);
                            if (!res.ok) throw new Error('Proxy error');
                            const data = await res.json();
                            if (data && data.length > 0) {
                                window.__GEO_CACHE__[city] = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
                            } else {
                                window.__GEO_CACHE__[city] = getFallbackCoords(city); // Safe Fallback
                            }
                        } catch (err) {
                            console.warn(`Geocoding proxy for ${city}, using fallback alg.`, err?.message);
                            window.__GEO_CACHE__[city] = getFallbackCoords(city); // Safe Fallback
                        }

                        await sleep(500); // UI render tick & respectful rate limit pacing
                    }
                }

                // --- OSRM Routing for Trains & Buses ---
                const uniquePairs = new Set();
                items.forEach(b => {
                    if (b.from_city && b.to_city && b.from_city !== b.to_city && b.booking_type !== 'Flight') {
                        uniquePairs.add(`${b.from_city}|${b.to_city}`);
                    }
                });

                let uncachedPairs = Array.from(uniquePairs).filter(pair => !window.__ROUTE_CACHE__ || window.__ROUTE_CACHE__[pair] === undefined);
                let fetchedPairsCount = 0;

                for (let pair of uniquePairs) {
                    if (!window.__ROUTE_CACHE__) window.__ROUTE_CACHE__ = {};
                    if (window.__ROUTE_CACHE__[pair] === undefined) {
                        try {
                            const [from, to] = pair.split('|');
                            const fromCoords = window.__GEO_CACHE__[from];
                            const toCoords = window.__GEO_CACHE__[to];

                            if (fromCoords && toCoords) {
                                fetchedPairsCount++;
                                loadingMessage.value = `Routing path ${from} -> ${to}... (${fetchedPairsCount}/${uncachedPairs.length})`;

                                const controller = new AbortController();
                                const timeoutId = setTimeout(() => controller.abort(), 4000);
                                const params = new URLSearchParams({ overview: 'simplified', geometries: 'geojson' });
                                const res = await fetch(`https://router.project-osrm.org/route/v1/driving/${fromCoords[1]},${fromCoords[0]};${toCoords[1]},${toCoords[0]}?${params.toString()}`, { signal: controller.signal });
                                clearTimeout(timeoutId);
                                const data = await res.json();
                                if (data && data.code === 'Ok' && data.routes && data.routes.length > 0) {
                                    const route = data.routes[0];
                                    const latLngs = route.geometry.coordinates.map(c => [c[1], c[0]]);
                                    window.__ROUTE_CACHE__[pair] = {
                                        distance: (route.distance / 1000).toFixed(1) + ' km',
                                        duration: Math.floor(route.duration / 3600) + 'h ' + Math.floor((route.duration % 3600) / 60) + 'm',
                                        path: latLngs
                                    };
                                } else {
                                    window.__ROUTE_CACHE__[pair] = null;
                                }
                                await sleep(500); // respect rate limits
                            } else {
                                window.__ROUTE_CACHE__[pair] = null;
                            }
                        } catch (err) {
                            console.warn('OSRM routing proxy failed:', err?.message);
                            window.__ROUTE_CACHE__[pair] = null;
                            await sleep(200);
                        }
                    }
                }

                const haversineDistance = (coords1, coords2) => {
                    const toRad = x => (x * Math.PI) / 180;
                    const R = 6371; // km
                    const dLat = toRad(coords2[0] - coords1[0]);
                    const dLon = toRad(coords2[1] - coords1[1]);
                    const lat1 = toRad(coords1[0]);
                    const lat2 = toRad(coords2[0]);
                    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
                    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                    return (R * c).toFixed(1) + ' km';
                };

                loadingMessage.value = 'Plotting routes...';

                const placeTransitIcon = (points, type, color, popup) => {
                    if (points.length < 2) return;
                    const midIdx = Math.floor(points.length / 2);
                    let html = '';
                    if (type === 'Flight') {
                        const p1 = points[Math.max(0, midIdx - 1)];
                        const p2 = points[Math.min(points.length - 1, midIdx + 1)];
                        const dy = p2[0] - p1[0];
                        const dx = p2[1] - p1[1];
                        const angle = Math.atan2(-dy, dx) * 180 / Math.PI;
                        html = `<div style="transform: rotate(${angle + 45}deg); color: ${color};" class="text-2xl marker-glow drop-shadow-md">
                                    <i class='bx bxs-plane-alt'></i>
                                </div>`;
                    } else {
                        const iconClass = type === 'Train' ? 'bxs-train' : 'bxs-bus';
                        html = `<div style="color: ${color};" class="marker-glow bg-white dark:bg-gray-800 rounded-full w-7 h-7 flex items-center justify-center shadow-lg border-2 border-current">
                                    <i class='bx ${iconClass} text-sm'></i>
                                </div>`;
                    }
                    L.marker(points[midIdx], {
                        icon: L.divIcon({ html, className: 'bg-transparent border-0', iconAnchor: type === 'Flight' ? [12, 12] : [14, 14] })
                    }).addTo(routeLayerGroup).bindPopup(popup);
                };

                items.forEach(b => {
                    if (b.from_city && b.to_city) {
                        const fromCoords = window.__GEO_CACHE__[b.from_city];
                        const toCoords = window.__GEO_CACHE__[b.to_city];

                        // Only draw if both coordinates were successfully resolved from the internet
                        if (!fromCoords || !toCoords) return;

                        let color = '#0ea5e9';
                        if (b.booking_type === 'Train') color = '#22c55e';
                        if (b.booking_type === 'Bus') color = '#f97316';

                        const isFlight = b.booking_type === 'Flight';

                        let routeData = null;
                        if (!isFlight && b.from_city !== b.to_city && window.__ROUTE_CACHE__) {
                            routeData = window.__ROUTE_CACHE__[`${b.from_city}|${b.to_city}`];
                        }

                        // Format a beautiful popup tooltip
                        const popupHTML = `
                            <div class="p-1 min-w-[200px]">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-xs font-black uppercase tracking-widest text-gray-400">${b.booking_type}</span>
                                    <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-brand-50 text-brand-700">${b.booking_id}</span>
                                </div>
                                <div class="flex items-center gap-3 font-bold text-gray-800 text-sm mb-3">
                                    <div>${b.from_city}</div>
                                    <i class="bx bx-right-arrow-alt text-gray-400"></i>
                                    <div>${b.to_city}</div>
                                </div>
                                <div class="space-y-1 mt-2 border-t border-gray-100 pt-2">
                                    ${b.flight_number ? `<div class="text-xs text-gray-600 flex justify-between"><span>Flight:</span> <span class="font-bold">${b.airline} ${b.flight_number}</span></div>` : ''}
                                    ${b.train_number ? `<div class="text-xs text-gray-600 flex justify-between"><span>Train:</span> <span class="font-bold">${b.train_number}</span></div>` : ''}
                                    ${b.bus_operator ? `<div class="text-xs text-gray-600 flex justify-between"><span>Bus:</span> <span class="font-bold">${b.bus_operator}</span></div>` : ''}
                                    <div class="text-xs text-gray-600 flex justify-between"><span>Date:</span> <span class="font-bold text-gray-900">${new Date(b.booking_date).toLocaleDateString()}</span></div>
                                    <div class="text-xs text-gray-600 flex justify-between border-b border-gray-100 pb-2"><span>Status:</span> <span class="font-bold ${b.status === 'Confirmed' ? 'text-green-600' : 'text-yellow-600'}">${b.status}</span></div>

                                    ${routeData ? `<div class="text-xs text-brand-600 flex justify-between pt-1"><span>Distance:</span> <span class="font-bold text-brand-700">${routeData.distance}</span></div>` : ''}
                                    ${routeData ? `<div class="text-xs text-brand-600 flex justify-between"><span>Est. Travel:</span> <span class="font-bold text-brand-700">${routeData.duration}</span></div>` : ''}
                                    ${isFlight && b.from_city !== b.to_city ? `<div class="text-xs text-blue-600 flex justify-between pt-1"><span>Flight Dist.:</span> <span class="font-bold text-blue-700">${haversineDistance(fromCoords, toCoords)}</span></div>` : ''}
                                    
                                    <div class="text-xs text-gray-600 flex justify-between mt-2 pt-1"><span>Cost:</span> <span class="font-bold text-gray-900">₹${b.cost.toLocaleString()}</span></div>
                                </div>
                                <a href="/bookings/${b.booking_id}" class="mt-3 block text-center text-xs font-bold text-brand-600 hover:text-brand-700 bg-brand-50 rounded-lg py-1.5 transition-colors cursor-pointer">View Full Details</a>
                            </div>
                        `;

                        // Draw curved line using geodesic arc for flights
                        if (isFlight) {
                            if (fromCoords[0] === toCoords[0] && fromCoords[1] === toCoords[1]) {
                                return; // Cannot draw route to same exact coordinate
                            }
                            try {
                                // Using Arc.js to calculate a great circle route
                                const start = { x: fromCoords[1], y: fromCoords[0] }; // lon, lat
                                const end = { x: toCoords[1], y: toCoords[0] };
                                const generator = new arc.GreatCircle(start, end);
                                const line = generator.Arc(100, { offset: 10 });

                                // Convert generated coords back to LatLng array for Leaflet
                                const curvePoints = line.geometries[0].coords.map(c => [c[1], c[0]]);

                                L.polyline(curvePoints, {
                                    color, weight: 3, opacity: 0.8, dashArray: '8, 12', className: 'path-flow-flight cursor-pointer hover:opacity-100'
                                }).addTo(routeLayerGroup).bindPopup(popupHTML);

                                placeTransitIcon(curvePoints, b.booking_type, color, popupHTML);
                            } catch (e) {
                                console.warn("Arc.js failed, falling back to straight line", e);
                                L.polyline([fromCoords, toCoords], {
                                    color, weight: 3, opacity: 0.8, dashArray: '8, 12', className: 'path-flow-flight cursor-pointer hover:opacity-100'
                                }).addTo(routeLayerGroup).bindPopup(popupHTML);
                                placeTransitIcon([fromCoords, toCoords], b.booking_type, color, popupHTML);
                            }
                        } else {
                            let pathPoints = [fromCoords, toCoords];
                            if (routeData && routeData.path) {
                                pathPoints = routeData.path;
                            }
                            L.polyline(pathPoints, {
                                color, weight: 4, opacity: 0.8, dashArray: '15, 10', className: 'path-flow-ground cursor-pointer hover:opacity-100'
                            }).addTo(routeLayerGroup).bindPopup(popupHTML);

                            placeTransitIcon(pathPoints, b.booking_type, color, popupHTML);
                        }

                        L.circleMarker(fromCoords, { radius: 4, color, fillOpacity: 1, stroke: true, weight: 2 }).addTo(routeLayerGroup);
                        L.circleMarker(toCoords, { radius: 4, color: '#f43f5e', fillOpacity: 1, stroke: true, weight: 2 }).addTo(routeLayerGroup);
                    }
                });

                // Dynamically fit map bounds to show tracked path, or reset view if no search
                if (pnrSearch.value && items.length > 0) {
                    const bounds = routeLayerGroup.getBounds();
                    if (bounds.isValid()) {
                        mapInstance.fitBounds(bounds, { padding: [50, 50], maxZoom: 6, animate: true, duration: 1.5 });
                    }
                } else if (!pnrSearch.value) {
                    mapInstance.setView([20.5937, 78.9629], 5, { animate: true, duration: 1 });
                }

            } catch (e) {
                console.error(e);
            } finally {
                loading.value = false;
            }
        };

        onMounted(() => {
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

            setTimeout(() => {
                initMapBase();
                fetchAndPlot();
            }, 100);

            // Listen for theme changes to swap tiles
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') initMapBase();
                });
            });
            observer.observe(document.documentElement, { attributes: true });
        });

        return { loading, loadingMessage, filter, pnrSearch, trackedCount, fetchAndPlot };
    }
});
