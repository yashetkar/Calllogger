/**
 * IT HELPDESK CALL LOGGER - FRONTEND LOGIC
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    let employeesMap = {};
    let editingTicketNo = null;
    let selectedTicketNo = null;
    let searchDebounceTimeout = null;

    // DOM Elements - Header
    const themeToggleBtn = document.getElementById("theme-toggle");
    const themeIcon = themeToggleBtn.querySelector(".theme-icon");

    // DOM Elements - Dashboard
    const totalCountEl = document.getElementById("metric-total");
    const openCountEl = document.getElementById("metric-open");
    const resolvedCountEl = document.getElementById("metric-resolved");

    // DOM Elements - Form
    const ticketForm = document.getElementById("ticket-form");
    const formTitleBadge = document.getElementById("form-mode");
    const ticketNoInput = document.getElementById("ticket_no");
    const logDateInput = document.getElementById("log_date");
    const callTimeInput = document.getElementById("call_time");
    const btnTimeNow = document.getElementById("btn-time-now");
    const employeeNameInput = document.getElementById("employee_name");
    const employeeEmailInput = document.getElementById("employee_email");
    const departmentSelect = document.getElementById("department");
    const engineerInput = document.getElementById("engineer");
    const engineerEmailInput = document.getElementById("engineer_email");
    const issueTypeSelect = document.getElementById("issue_type");
    const prioritySelect = document.getElementById("priority");
    const statusSelect = document.getElementById("status");
    const resolvedDateInput = document.getElementById("resolved_date");
    const resolvedTimeInput = document.getElementById("resolved_time");
    const btnResolvedNow = document.getElementById("btn-resolved-now");
    const issueTextarea = document.getElementById("issue");
    const remarksTextarea = document.getElementById("remarks");

    const btnSave = document.getElementById("btn-save");
    const btnClear = document.getElementById("btn-clear");
    const btnOpenSettings = document.getElementById("btn-open-settings");

    // DOM Elements - Table & Controls
    const btnEdit = document.getElementById("btn-edit");
    const btnResendEmail = document.getElementById("btn-resend-email");
    const btnDelete = document.getElementById("btn-delete");
    const btnExport = document.getElementById("btn-export");
    const searchInput = document.getElementById("search-input");
    const statusFilter = document.getElementById("status-filter");
    const ticketsTbody = document.getElementById("tickets-tbody");
    const noDataEl = document.getElementById("no-data");

    // DOM Elements - Calendar Pickers & Search
    const btnDateCalendar = document.getElementById("btn-date-calendar");
    const logDatePicker = document.getElementById("log_date_picker");
    const btnResolvedDateCalendar = document.getElementById("btn-resolved-date-calendar");
    const resolvedDatePicker = document.getElementById("resolved_date_picker");
    const btnSearchSubmit = document.getElementById("btn-search-submit");

    // DOM Elements - Email Settings Modal
    const settingsModal = document.getElementById("settings-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const settingsForm = document.getElementById("settings-form");
    const emailEnabledCheckbox = document.getElementById("email_enabled");
    const smtpHostInput = document.getElementById("smtp_host");
    const smtpPortInput = document.getElementById("smtp_port");
    const smtpUserInput = document.getElementById("smtp_user");
    const smtpPasswordInput = document.getElementById("smtp_password");
    const smtpUseTlsCheckbox = document.getElementById("smtp_use_tls");
    const testRecipientInput = document.getElementById("test_recipient");
    const btnTestConnection = document.getElementById("btn-test-connection");
    const btnSaveSettings = document.getElementById("btn-save-settings");
    const btnCancelSettings = document.getElementById("btn-cancel-settings");

    // DOM Elements - Toast
    const toastEl = document.getElementById("toast");

    // ==========================================
    // INITIALIZATION & THEME CONFIG
    // ==========================================
    const init = async () => {
        setupTheme();
        setupClock();
        await fetchDropdownData();
        await fetchEmployees();
        await loadDashboard();
        await loadTickets();
        resetForm();
    };

    const setupTheme = () => {
        const savedTheme = localStorage.getItem("theme") || "light";
        document.documentElement.setAttribute("data-theme", savedTheme);
        
        const sunSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></svg>`;
        const moonSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
        
        themeIcon.innerHTML = savedTheme === "dark" ? sunSvg : moonSvg;

        // Set initial theme color for title bar
        const metaThemeColor = document.getElementById("meta-theme-color");
        if (metaThemeColor) {
            metaThemeColor.setAttribute("content", savedTheme === "dark" ? "#080b11" : "#f1f5f9");
        }
        
        themeToggleBtn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
            themeIcon.innerHTML = newTheme === "dark" ? sunSvg : moonSvg;

            // Dynamically update theme color for title bar
            if (metaThemeColor) {
                metaThemeColor.setAttribute("content", newTheme === "dark" ? "#080b11" : "#f1f5f9");
            }
        });
    };

    const setupClock = () => {
        const clockEl = document.getElementById("header-clock");
        if (!clockEl) return;
        
        const updateClock = () => {
            const now = new Date();
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            const hourStr = String(hours).padStart(2, '0');
            clockEl.textContent = `${hourStr}:${minutes}:${seconds} ${ampm}`;
        };
        
        updateClock();
        setInterval(updateClock, 1000);
    };

    // ==========================================
    // API CALLS
    // ==========================================
    const fetchDropdownData = async () => {
        try {
            const res = await fetch("/api/meta");
            const data = await res.json();

            // Populate departments
            departmentSelect.innerHTML = "";
            data.departments.forEach(dept => {
                const opt = document.createElement("option");
                opt.value = dept;
                opt.textContent = dept;
                departmentSelect.appendChild(opt);
            });

            // Populate issue types
            issueTypeSelect.innerHTML = "";
            data.issue_types.forEach(type => {
                const opt = document.createElement("option");
                opt.value = type;
                opt.textContent = type;
                issueTypeSelect.appendChild(opt);
            });

            // Set current defaults
            logDateInput.value = data.current_date;
            callTimeInput.value = data.current_time;
            ticketNoInput.value = data.next_ticket;
        } catch (e) {
            showToast("Failed to load metadata from server.", "error");
        }
    };

    const fetchEmployees = async () => {
        try {
            const res = await fetch("/api/employees");
            employeesMap = await res.json();
        } catch (e) {
            console.error("Failed to load employee list suggestions", e);
        }
    };

    const loadDashboard = async () => {
        try {
            const res = await fetch("/api/dashboard");
            const counts = await res.json();
            totalCountEl.textContent = counts.total;
            openCountEl.textContent = counts.open;
            resolvedCountEl.textContent = counts.resolved;
        } catch (e) {
            console.error("Failed to load dashboard metrics", e);
        }
    };

    const loadTickets = async () => {
        const query = searchInput.value.trim();
        const status = statusFilter.value;
        try {
            const res = await fetch(`/api/tickets?search=${encodeURIComponent(query)}&status=${encodeURIComponent(status)}`);
            const tickets = await res.json();

            ticketsTbody.innerHTML = "";
            if (tickets.length === 0) {
                noDataEl.classList.remove("hidden");
                return;
            }
            noDataEl.classList.add("hidden");

            tickets.forEach(t => {
                const tr = document.createElement("tr");
                
                const statusClass = t.status.replace(/\s+/g, '-').toLowerCase();
                tr.classList.add(`tag-${statusClass}`);
                
                if (selectedTicketNo === t.ticket_no) tr.classList.add("selected");

                const priorityClass = t.priority.toLowerCase();
                const priorityBadge = `<span class="badge badge-priority-${priorityClass}">${t.priority}</span>`;
                const statusBadge = `<span class="badge badge-status-${statusClass}">${t.status}</span>`;

                let ratingBadge = `<span style="color:var(--text-muted);">-</span>`;
                if (t.rating === "Excellent") {
                    ratingBadge = `<span style="color:#16a34a; font-weight:600;">👍 Excellent</span>`;
                } else if (t.rating === "Poor") {
                    ratingBadge = `<span style="color:#dc2626; font-weight:600;">👎 Poor</span>`;
                }

                tr.innerHTML = `
                    <td><strong>${t.ticket_no}</strong></td>
                    <td>${t.employee_name}</td>
                    <td>${t.log_date}</td>
                    <td>${t.call_time}</td>
                    <td>${t.resolved_date || "-"}</td>
                    <td>${t.resolved_time || "-"}</td>
                    <td>${t.department}</td>
                    <td class="cell-issue">${t.issue}</td>
                    <td>${t.issue_type}</td>
                    <td>${priorityBadge}</td>
                    <td>${statusBadge}</td>
                    <td>${ratingBadge}</td>
                    <td>${t.engineer}</td>
                `;

                // Single click selects a row
                tr.addEventListener("click", () => {
                    document.querySelectorAll("#tickets-table tbody tr").forEach(row => row.classList.remove("selected"));
                    tr.classList.add("selected");
                    selectedTicketNo = t.ticket_no;
                });

                // Double click loads into editor
                tr.addEventListener("dblclick", () => {
                    loadTicketForEditing(t.ticket_no);
                });

                ticketsTbody.appendChild(tr);
            });
        } catch (e) {
            showToast("Failed to load tickets list.", "error");
        }
    };

    // ==========================================
    // AUTOCOMPLETE IMPLEMENTATION
    // ==========================================
    employeeNameInput.addEventListener("input", function() {
        const val = this.value.trim().toLowerCase();
        closeAutocompleteList();
        if (!val) return;

        const listDiv = document.getElementById("autocomplete-list");
        const matches = Object.keys(employeesMap)
            .filter(nameKey => nameKey.includes(val))
            .slice(0, 15);

        matches.forEach(matchKey => {
            const emp = employeesMap[matchKey];
            const itemDiv = document.createElement("div");
            const lowerName = emp.name.toLowerCase();
            const idx = lowerName.indexOf(val);
            if (idx !== -1) {
                const before = emp.name.substring(0, idx);
                const match = emp.name.substring(idx, idx + val.length);
                const after = emp.name.substring(idx + val.length);
                itemDiv.innerHTML = `${before}<strong>${match}</strong>${after}`;
            } else {
                itemDiv.textContent = emp.name;
            }
            itemDiv.innerHTML += ` <span style="font-size:0.75rem; color:var(--text-muted);">(${emp.department})</span>`;
            itemDiv.addEventListener("click", () => {
                employeeNameInput.value = emp.name;
                employeeEmailInput.value = emp.email;
                departmentSelect.value = emp.department;
                closeAutocompleteList();
            });
            listDiv.appendChild(itemDiv);
        });
    });

    const closeAutocompleteList = () => {
        const listDiv = document.getElementById("autocomplete-list");
        if (listDiv) listDiv.innerHTML = "";
    };

    document.addEventListener("click", (e) => {
        if (e.target !== employeeNameInput) {
            closeAutocompleteList();
        }
    });

    // Auto fill on focus out if matches exactly
    employeeNameInput.addEventListener("blur", () => {
        setTimeout(() => {
            const val = employeeNameInput.value.trim().toLowerCase();
            if (employeesMap[val]) {
                const emp = employeesMap[val];
                employeeEmailInput.value = emp.email;
                departmentSelect.value = emp.department;
            }
        }, 150);
    });

    // ==========================================
    // FORM BEHAVIORS
    // ==========================================
    
    // Status change auto dates & progressive disclosure toggle
    statusSelect.addEventListener("change", () => {
        const status = statusSelect.value;
        const todayStr = getTodayDateString();
        const timeStr = getCurrentTimeString();
        const resolvedSec = document.getElementById("resolved-section");

        if (status === "Resolved" || status === "Closed") {
            resolvedSec.classList.remove("hidden");
            if (!resolvedDateInput.value.trim()) {
                resolvedDateInput.value = todayStr;
            }
            if (!resolvedTimeInput.value.trim()) {
                resolvedTimeInput.value = timeStr;
            }
        } else {
            resolvedSec.classList.add("hidden");
            resolvedDateInput.value = "";
            resolvedTimeInput.value = "";
            remarksTextarea.value = "";
        }
    });

    btnTimeNow.addEventListener("click", () => {
        callTimeInput.value = getCurrentTimeString();
    });

    btnResolvedNow.addEventListener("click", () => {
        resolvedTimeInput.value = getCurrentTimeString();
        if (!resolvedDateInput.value.trim()) {
            resolvedDateInput.value = getTodayDateString();
        }
    });

    const getTodayDateString = () => {
        const today = new Date();
        const d = String(today.getDate()).padStart(2, '0');
        const m = String(today.getMonth() + 1).padStart(2, '0');
        const y = today.getFullYear();
        return `${d}-${m}-${y}`;
    };

    const getCurrentTimeString = () => {
        const today = new Date();
        let hours = today.getHours();
        const minutes = String(today.getMinutes()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        const hourStr = String(hours).padStart(2, '0');
        return `${hourStr}:${minutes} ${ampm}`;
    };

    const resetForm = async () => {
        ticketForm.reset();
        editingTicketNo = null;
        formTitleBadge.textContent = "NEW TICKET";
        formTitleBadge.style.backgroundColor = "var(--tag-open-bg)";
        formTitleBadge.style.color = "var(--tag-open-text)";
        
        // Reset inputs and reload metadata for next ticket no
        await fetchDropdownData();
        
        // Ensure priority defaults to High
        prioritySelect.value = "High";
        statusSelect.value = "In Progress";
        resolvedDateInput.value = "";
        resolvedTimeInput.value = "";
        
        // Hide resolved section by default
        document.getElementById("resolved-section").classList.add("hidden");
    };

    const loadTicketForEditing = async (ticketNo) => {
        try {
            const res = await fetch(`/api/tickets/${ticketNo}`);
            if (!res.ok) {
                const errMsg = await handleNonOkResponse(res, "Failed to load ticket details");
                showToast(errMsg, "error");
                return;
            }
            const t = await res.json();

            // Populate form
            editingTicketNo = t.ticket_no;
            ticketNoInput.value = t.ticket_no;
            logDateInput.value = t.log_date;
            callTimeInput.value = t.call_time;
            employeeNameInput.value = t.employee_name;
            employeeEmailInput.value = t.employee_email || "";
            departmentSelect.value = t.department;
            engineerInput.value = t.engineer;
            engineerEmailInput.value = t.engineer_email || "";
            issueTypeSelect.value = t.issue_type;
            prioritySelect.value = t.priority;
            statusSelect.value = t.status;
            resolvedDateInput.value = t.resolved_date || "";
            resolvedTimeInput.value = t.resolved_time || "";
            issueTextarea.value = t.issue;
            remarksTextarea.value = t.remarks || "";

            // Toggle resolved section based on loaded status
            const resolvedSec = document.getElementById("resolved-section");
            if (t.status === "Resolved" || t.status === "Closed") {
                resolvedSec.classList.remove("hidden");
            } else {
                resolvedSec.classList.add("hidden");
            }

            formTitleBadge.textContent = `EDITING: ${t.ticket_no}`;
            formTitleBadge.style.backgroundColor = "var(--tag-high-bg)";
            formTitleBadge.style.color = "var(--tag-high-text)";
            
            showToast(`Loaded ticket ${t.ticket_no} for editing.`, "info");
            
            // Scroll form into view for mobile devices
            ticketForm.scrollIntoView({ behavior: 'smooth' });
        } catch (e) {
            showToast("Error loading ticket detail.", "error");
        }
    };

    // ==========================================
    // CRUD EVENT HANDLERS
    // ==========================================

    // Save
    ticketForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const payload = {
            ticket_no: editingTicketNo, // Will generate if null
            log_date: logDateInput.value.trim(),
            call_time: callTimeInput.value.trim(),
            employee_name: employeeNameInput.value.trim(),
            employee_email: employeeEmailInput.value.trim(),
            department: departmentSelect.value,
            engineer: engineerInput.value.trim(),
            engineer_email: engineerEmailInput.value.trim(),
            issue_type: issueTypeSelect.value,
            priority: prioritySelect.value,
            status: statusSelect.value,
            resolved_date: resolvedDateInput.value.trim(),
            resolved_time: resolvedTimeInput.value.trim(),
            issue: issueTextarea.value.trim(),
            remarks: remarksTextarea.value.trim()
        };

        // Validate formats
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (payload.employee_email && !emailPattern.test(payload.employee_email)) {
            showToast("Invalid Employee Email format.", "error");
            return;
        }
        if (payload.engineer_email && !emailPattern.test(payload.engineer_email)) {
            showToast("Invalid Engineer Email format.", "error");
            return;
        }

        const timePattern = /^(0[1-9]|1[0-2]):[0-5][0-9] (AM|PM)$/i;
        if (!timePattern.test(payload.call_time)) {
            showToast("Call Time must be 12-hour format with AM/PM (e.g. 09:30 AM).", "error");
            return;
        }
        if (payload.resolved_time && !timePattern.test(payload.resolved_time)) {
            showToast("Resolved Time must be 12-hour format with AM/PM (e.g. 05:45 PM).", "error");
            return;
        }

        const datePattern = /^[0-3][0-9]-[0-1][0-9]-\d{4}$/;
        if (!datePattern.test(payload.log_date)) {
            showToast("Date must be in format DD-MM-YYYY.", "error");
            return;
        }
        if (payload.resolved_date && !datePattern.test(payload.resolved_date)) {
            showToast("Resolved Date must be in format DD-MM-YYYY.", "error");
            return;
        }

        try {
            const res = await fetch("/api/tickets", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                showToast(`Ticket saved successfully! (${data.ticket_no})`, "success");
                resetForm();
                await loadTickets();
                await loadDashboard();
                await fetchEmployees();
            } else {
                const errMsg = await handleNonOkResponse(res, "Failed to save ticket record.");
                showToast(errMsg, "error");
            }
        } catch (err) {
            showToast("Network error trying to save ticket.", "error");
        }
    });

    // Clear Form
    btnClear.addEventListener("click", resetForm);

    // Edit Selected Button
    btnEdit.addEventListener("click", () => {
        if (!selectedTicketNo) {
            showToast("Please select a ticket from the log table first.", "error");
            return;
        }
        loadTicketForEditing(selectedTicketNo);
    });

    // Resend Email Notification
    if (btnResendEmail) {
        btnResendEmail.addEventListener("click", async () => {
            if (!selectedTicketNo) {
                showToast("Please select a ticket from the log table first.", "error");
                return;
            }
            try {
                showToast(`Resending email notification for ${selectedTicketNo}...`, "info");
                const res = await fetch(`/api/tickets/${selectedTicketNo}/resend_email`, { method: "POST" });
                if (res.ok) {
                    const data = await res.json();
                    showToast(data.message || `Email notification sent for ${selectedTicketNo}!`, "success");
                } else {
                    const errMsg = await handleNonOkResponse(res, "Failed to resend email.");
                    showToast(errMsg, "error");
                }
            } catch (e) {
                showToast("Network error trying to resend email.", "error");
            }
        });
    }

    // Delete Selected
    btnDelete.addEventListener("click", async () => {
        if (!selectedTicketNo) {
            showToast("Please select a ticket from the log table first.", "error");
            return;
        }

        const confirmDelete = confirm(`Are you sure you want to delete ticket ${selectedTicketNo}?`);
        if (!confirmDelete) return;

        try {
            const res = await fetch(`/api/tickets/${selectedTicketNo}`, { method: "DELETE" });

            if (res.ok) {
                const data = await res.json();
                showToast(`Ticket ${selectedTicketNo} soft-deleted. Logged in history list.`, "success");
                if (editingTicketNo === selectedTicketNo) {
                    resetForm();
                }
                selectedTicketNo = null;
                await loadTickets();
                await loadDashboard();
            } else {
                const errMsg = await handleNonOkResponse(res, "Failed to delete ticket.");
                showToast(errMsg, "error");
            }
        } catch (e) {
            showToast("Network error trying to delete ticket.", "error");
        }
    });

    // Export Excel
    btnExport.addEventListener("click", async () => {
        try {
            showToast("Generating Excel file report...", "info");
            const res = await fetch("/api/export", { method: "POST" });
            
            if (!res.ok) {
                const errMsg = await handleNonOkResponse(res, "Failed to export Excel.");
                showToast(errMsg, "error");
                return;
            }

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `call_logs_${getTodayDateString().replace(/-/g, "")}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showToast("Excel export file downloaded.", "success");
        } catch (e) {
            showToast("Network error exporting data.", "error");
        }
    });

    // ==========================================
    // FILTER & SEARCH ACTIONS
    // ==========================================
    const debouncedSearch = () => {
        clearTimeout(searchDebounceTimeout);
        searchDebounceTimeout = setTimeout(() => {
            loadTickets();
        }, 250);
    };

    searchInput.addEventListener("input", debouncedSearch);
    statusFilter.addEventListener("change", loadTickets);

    // ==========================================
    // EMAIL SETTINGS MODAL ACTIONS
    // ==========================================
    btnOpenSettings.addEventListener("click", async () => {
        try {
            // Load current settings from API
            const res = await fetch("/api/settings");
            if (!res.ok) {
                const errMsg = await handleNonOkResponse(res, "Failed to load SMTP settings.");
                showToast(errMsg, "error");
                return;
            }
            const s = await res.json();

            emailEnabledCheckbox.checked = s.email_enabled;
            smtpHostInput.value = s.smtp_host || "";
            smtpPortInput.value = s.smtp_port || "";
            smtpUserInput.value = s.smtp_user || "";
            smtpPasswordInput.value = s.smtp_password || "";
            smtpUseTlsCheckbox.checked = s.smtp_use_tls;
            testRecipientInput.value = "";

            settingsModal.classList.remove("hidden");
        } catch (e) {
            showToast("Failed to load SMTP settings: " + (e.message || e), "error");
        }
    });

    const closeModal = () => {
        settingsModal.classList.add("hidden");
    };

    btnCloseModal.addEventListener("click", closeModal);
    btnCancelSettings.addEventListener("click", closeModal);

    // Save settings
    btnSaveSettings.addEventListener("click", async () => {
        const payload = {
            email_enabled: emailEnabledCheckbox.checked,
            smtp_host: smtpHostInput.value.trim(),
            smtp_port: parseInt(smtpPortInput.value.trim()),
            smtp_user: smtpUserInput.value.trim(),
            smtp_password: smtpPasswordInput.value,
            smtp_use_tls: smtpUseTlsCheckbox.checked
        };

        if (payload.email_enabled && (!payload.smtp_host || !payload.smtp_port || !payload.smtp_user || !payload.smtp_password)) {
            showToast("If notifications are enabled, all SMTP fields must be filled.", "error");
            return;
        }

        try {
            const res = await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                const data = await res.json();
                if (data.success) {
                    showToast("SMTP settings saved successfully.", "success");
                    closeModal();
                } else {
                    showToast(data.error || "Failed to save settings.", "error");
                }
            } else {
                const errMsg = await handleNonOkResponse(res, "Failed to save settings.");
                showToast(errMsg, "error");
            }
        } catch (e) {
            showToast("Network error saving settings.", "error");
        }
    });

    // Test connection
    btnTestConnection.addEventListener("click", async () => {
        const payload = {
            smtp_host: smtpHostInput.value.trim(),
            smtp_port: smtpPortInput.value.trim(),
            smtp_user: smtpUserInput.value.trim(),
            smtp_password: smtpPasswordInput.value,
            smtp_use_tls: smtpUseTlsCheckbox.checked,
            test_recipient: testRecipientInput.value.trim()
        };

        if (!payload.smtp_host || !payload.smtp_port || !payload.smtp_user || !payload.smtp_password || !payload.test_recipient) {
            showToast("Please fill all SMTP fields and the Test Recipient Email.", "error");
            return;
        }

        btnTestConnection.disabled = true;
        btnTestConnection.textContent = "⚡ TESTING...";

        try {
            const res = await fetch("/api/settings/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                const data = await res.json();
                if (data.success) {
                    alert("SMTP Connection succeeded! Check the test recipient's inbox.");
                    showToast("SMTP Test connection successful!", "success");
                } else {
                    alert(`SMTP Connection failed:\n${data.error}`);
                    showToast("SMTP Connection failed.", "error");
                }
            } else {
                const errMsg = await handleNonOkResponse(res, "SMTP Connection failed.");
                alert(`SMTP Connection failed:\n${errMsg}`);
                showToast(errMsg, "error");
            }
        } catch (e) {
            showToast("Error communicating during test.", "error");
        } finally {
            btnTestConnection.disabled = false;
            btnTestConnection.textContent = "⚡ TEST CONNECTION";
        }
    });

    // ==========================================
    // TOAST NOTIFICATIONS
    // ==========================================
    const handleNonOkResponse = async (response, defaultMessage) => {
        try {
            const err = await response.json();
            return err.error || defaultMessage;
        } catch (e) {
            return defaultMessage;
        }
    };

    const showToast = (message, type = "success") => {
        toastEl.className = `toast ${type}`;
        
        let iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>`;
        if (type === "success") {
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`;
        } else if (type === "error") {
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
        } else if (type === "info") {
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 16px; height: 16px;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
        }

        toastEl.innerHTML = `<span style="display: flex; align-items: center;">${iconSvg}</span> <span>${message}</span>`;
        toastEl.classList.remove("hidden");

        setTimeout(() => {
            toastEl.classList.add("hidden");
        }, 4000);
    };

    // ==========================================
    // EXTRA EVENT HANDLERS & HELPERS
    // ==========================================
    const formatDateToDDMMYYYY = (dateStr) => {
        if (!dateStr) return "";
        if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) return dateStr;
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
            const parts = dateStr.split("-");
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        return dateStr;
    };

    const formatDateToYYYYMMDD = (dateStr) => {
        if (!dateStr) return "";
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
        if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) {
            const parts = dateStr.split("-");
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        return dateStr;
    };

    if (btnDateCalendar && logDatePicker) {
        btnDateCalendar.addEventListener("click", () => {
            const val = logDateInput.value.trim();
            if (val) {
                logDatePicker.value = formatDateToYYYYMMDD(val);
            }
            logDatePicker.showPicker();
        });
        logDatePicker.addEventListener("change", () => {
            logDateInput.value = formatDateToDDMMYYYY(logDatePicker.value);
        });
    }

    if (btnResolvedDateCalendar && resolvedDatePicker) {
        btnResolvedDateCalendar.addEventListener("click", () => {
            const val = resolvedDateInput.value.trim();
            if (val) {
                resolvedDatePicker.value = formatDateToYYYYMMDD(val);
            }
            resolvedDatePicker.showPicker();
        });
        resolvedDatePicker.addEventListener("change", () => {
            resolvedDateInput.value = formatDateToDDMMYYYY(resolvedDatePicker.value);
        });
    }

    if (btnSearchSubmit) {
        btnSearchSubmit.addEventListener("click", loadTickets);
    }

    // Bootstrap app
    init();
});
