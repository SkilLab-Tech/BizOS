// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Networking Connection", {
	refresh(frm) {
		// Add action buttons for pending connections
		if (frm.doc.status === "Pending" && !frm.is_new()) {
			frm.add_custom_button(__("Accept Connection"), function () {
				frappe.call({
					method: "frappe.networking.doctype.networking_connection.networking_connection.accept_connection",
					args: {
						connection_name: frm.doc.name,
					},
					callback: function (r) {
						if (r.message) {
							frm.reload_doc();
							frappe.show_alert({
								message: __("Connection Accepted"),
								indicator: "green",
							});
						}
					},
				});
			});

			frm.add_custom_button(__("Reject Connection"), function () {
				frappe.confirm(
					__("Are you sure you want to reject this connection request?"),
					function () {
						frappe.call({
							method: "frappe.networking.doctype.networking_connection.networking_connection.reject_connection",
							args: {
								connection_name: frm.doc.name,
							},
							callback: function (r) {
								if (r.message) {
									frm.reload_doc();
									frappe.show_alert({
										message: __("Connection Rejected"),
										indicator: "red",
									});
								}
							},
						});
					}
				);
			});
		}

		// Add schedule meeting button for accepted connections
		if (frm.doc.status === "Accepted" && !frm.is_new()) {
			frm.add_custom_button(__("Schedule Meeting"), function () {
				frappe.new_doc("Networking Meeting", {
					connection: frm.doc.name,
					participant_1: frm.doc.from_member,
					participant_2: frm.doc.to_member,
				});
			});
		}

		// Set query for member fields
		frm.set_query("from_member", function () {
			return {
				filters: {
					status: "Active",
				},
			};
		});

		frm.set_query("to_member", function () {
			return {
				filters: {
					status: "Active",
					name: ["!=", frm.doc.from_member],
				},
			};
		});

		// Show member profile links
		if (frm.doc.from_member) {
			frm.add_custom_button(
				__("View {0}", [frm.doc.from_member_name || frm.doc.from_member]),
				function () {
					frappe.set_route("Form", "Member Profile", frm.doc.from_member);
				},
				__("Members")
			);
		}

		if (frm.doc.to_member) {
			frm.add_custom_button(
				__("View {0}", [frm.doc.to_member_name || frm.doc.to_member]),
				function () {
					frappe.set_route("Form", "Member Profile", frm.doc.to_member);
				},
				__("Members")
			);
		}
	},
});
