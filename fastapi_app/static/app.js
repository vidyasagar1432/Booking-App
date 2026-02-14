const { createApp } = Vue;

function blankForm() {
  const today = new Date().toISOString().slice(0, 10);
  return {
    booking_mode: "flight",
    booking_id: "",
    booking_date: today,
    status: "pending",
    company_name: "",
    email: "",
    phone: "",
    vendor: "",
    passenger_name: "",
    guest_name: "",
    passengers: "",
    passenger_count: 0,
    guests: "",
    guests_count: 0,
    airline: "",
    pnr_eticket_no: "",
    trip_type: "",
    from_airport: "",
    to_airport: "",
    hotel_name: "",
    city: "",
    check_in_date: "",
    check_out_date: "",
    number_of_nights: 0,
    room_type: "",
    number_of_rooms: 0,
    train_name: "",
    train_number: "",
    from_station: "",
    to_station: "",
    coach: "",
    bus_company: "",
    bus_pnr: "",
    from_city: "",
    to_city: "",
    departure_date: "",
    departure_time: "",
    arrival_date: "",
    arrival_time: "",
    seat_number: "",
    travel_class: "",
    total_cost: 0,
    notes: "",
  };
}

createApp({
  data() {
    return {
      tab: "bookings",
      bookings: [],
      summary: {},
      form: blankForm(),
      filters: { search: "", booking_mode: "", status: "" },
      page: 1,
      pageSize: 10,
      meta: { total: 0, total_pages: 0 },
      editing: {},
      editingJson: "",
      loading: false,
      formLoading: false,
      error: "",
      success: "",
      ws: null,
      heartbeat: null,
      refreshTimer: null,
    };
  },
  computed: {
    hasRows() {
      return this.bookings.length > 0;
    },
    canPrev() {
      return this.page > 1;
    },
    canNext() {
      return this.page < (this.meta.total_pages || 1);
    },
  },
  methods: {
    clearFlash() {
      this.error = "";
      this.success = "";
    },
    setError(message) {
      this.success = "";
      this.error = message || "Something went wrong.";
    },
    setSuccess(message) {
      this.error = "";
      this.success = message;
    },
    cleanPayload(obj) {
      return Object.fromEntries(
        Object.entries(obj).filter(([, v]) => v !== "" && v !== null && v !== undefined)
      );
    },
    async request(url, options = {}) {
      const res = await fetch(url, options);
      const body = await res.json().catch(() => ({}));
      if (!res.ok || body.success === false) {
        const apiMessage = body?.error?.message || body?.message || `HTTP ${res.status}`;
        throw new Error(apiMessage);
      }
      return body;
    },
    async loadAll({ silent = false } = {}) {
      if (!silent) {
        this.loading = true;
      }
      try {
        const params = new URLSearchParams();
        Object.entries(this.filters).forEach(([k, v]) => v && params.set(k, v));
        params.set("page", String(this.page));
        params.set("page_size", String(this.pageSize));

        const [bookingsRes, summaryRes] = await Promise.all([
          this.request(`/api/bookings?${params.toString()}`),
          this.request(`/api/admin/summary`),
        ]);

        this.bookings = bookingsRes.data || [];
        this.meta = bookingsRes.meta || { total: 0, total_pages: 0 };
        this.summary = summaryRes.data || {};
      } catch (err) {
        this.setError(err.message);
      } finally {
        this.loading = false;
      }
    },
    async createBooking() {
      this.formLoading = true;
      this.clearFlash();
      try {
        await this.request("/api/bookings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.cleanPayload(this.form)),
        });
        this.form = blankForm();
        this.page = 1;
        await this.loadAll();
        this.setSuccess("Booking created successfully.");
      } catch (err) {
        this.setError(err.message);
      } finally {
        this.formLoading = false;
      }
    },
    async patchBooking(id, patch) {
      this.clearFlash();
      try {
        await this.request(`/api/bookings/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
        });
        await this.loadAll({ silent: true });
        this.setSuccess("Booking updated.");
      } catch (err) {
        this.setError(err.message);
      }
    },
    async deleteBooking(id) {
      this.clearFlash();
      if (!window.confirm("Delete this booking?")) {
        return;
      }
      try {
        await this.request(`/api/bookings/${id}`, { method: "DELETE" });
        if (this.bookings.length === 1 && this.page > 1) {
          this.page -= 1;
        }
        await this.loadAll();
        this.setSuccess("Booking deleted.");
      } catch (err) {
        this.setError(err.message);
      }
    },
    startEdit(booking) {
      this.editing = booking;
      this.editingJson = JSON.stringify(booking, null, 2);
      this.clearFlash();
    },
    cancelEdit() {
      this.editing = {};
      this.editingJson = "";
    },
    async saveEdit() {
      try {
        const parsed = JSON.parse(this.editingJson);
        delete parsed.id;
        delete parsed.created_at;
        delete parsed.updated_at;
        await this.patchBooking(this.editing.id, parsed);
        this.cancelEdit();
      } catch {
        this.setError("Invalid JSON in edit payload.");
      }
    },
    async applyFilters() {
      this.page = 1;
      await this.loadAll();
    },
    async prevPage() {
      if (!this.canPrev) return;
      this.page -= 1;
      await this.loadAll();
    },
    async nextPage() {
      if (!this.canNext) return;
      this.page += 1;
      await this.loadAll();
    },
    connectWs() {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      this.ws = new WebSocket(`${protocol}://${window.location.host}/ws`);

      this.ws.onopen = () => {
        // Keep the socket open in environments with aggressive idle timeouts.
        this.heartbeat = setInterval(() => {
          if (this.ws?.readyState === 1) {
            this.ws.send("ping");
          }
        }, 20000);
      };
      this.ws.onmessage = async () => {
        await this.loadAll({ silent: true });
      };
      this.ws.onerror = () => {
        this.setError("Live update connection error. Falling back to auto refresh.");
      };
      this.ws.onclose = () => {
        clearInterval(this.heartbeat);
        setTimeout(() => this.connectWs(), 1500);
      };
    },
  },
  mounted() {
    this.loadAll();
    this.connectWs();
    this.refreshTimer = setInterval(() => this.loadAll({ silent: true }), 10000);
  },
  beforeUnmount() {
    clearInterval(this.refreshTimer);
    clearInterval(this.heartbeat);
    if (this.ws) {
      this.ws.close();
    }
  },
}).mount("#app");
