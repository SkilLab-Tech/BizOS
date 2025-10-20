// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member Profile", {
	refresh(frm) {
		// Add custom buttons
		if (!frm.is_new()) {
			// Find Matches button
			if (frm.doc.ai_matching_enabled && frm.doc.status === "Active") {
				frm.add_custom_button(__("Find Matches"), function () {
					frappe.call({
						method: "frappe.networking.doctype.member_profile.member_profile.find_matching_members",
						args: {
							member_profile: frm.doc.name,
							limit: 20,
						},
						callback: function (r) {
							if (r.message && r.message.length > 0) {
								show_matches_dialog(frm, r.message);
							} else {
								frappe.msgprint(__("No matches found based on your criteria."));
							}
						},
					});
				});
			}

			// View Profile button (opens web view if available)
			frm.add_custom_button(__("View Public Profile"), function () {
				frappe.msgprint(__("Public profile view will be available once web templates are set up."));
			});

			// Contact button
			if (frm.doc.email) {
				frm.add_custom_button(__("Send Email"), function () {
					frappe.call({
						method: "frappe.core.doctype.communication.email.make",
						args: {
							recipients: frm.doc.email,
							subject: __("Hello from {0}", [frappe.session.user_fullname]),
							doctype: "Member Profile",
							name: frm.doc.name,
						},
					});
				});
			}

			// Request Connection button
			frm.add_custom_button(__("Request Connection"), function () {
				frappe.new_doc("Networking Connection", {
					from_member: frappe.session.user,
					to_member: frm.doc.name,
					status: "Pending",
				});
			});
		}

		// Set query for user field
		frm.set_query("user", function () {
			return {
				filters: {
					enabled: 1,
				},
			};
		});

		// Set query for contact field
		frm.set_query("contact", function () {
			return {
				filters: {
					email_id: frm.doc.email,
				},
			};
		});

		// Show statistics
		if (!frm.is_new()) {
			show_member_stats(frm);
		}
	},

	email(frm) {
		// Auto-link user when email changes
		if (frm.doc.email && !frm.doc.user) {
			frappe.db.get_value("User", { email: frm.doc.email }, "name", (r) => {
				if (r && r.name) {
					frm.set_value("user", r.name);
				}
			});
		}

		// Auto-link contact when email changes
		if (frm.doc.email && !frm.doc.contact) {
			frappe.db.get_value("Contact", { email_id: frm.doc.email }, "name", (r) => {
				if (r && r.name) {
					frm.set_value("contact", r.name);
				}
			});
		}
	},

	first_name(frm) {
		update_full_name(frm);
	},

	middle_name(frm) {
		update_full_name(frm);
	},

	last_name(frm) {
		update_full_name(frm);
	},
});

function update_full_name(frm) {
	let parts = [frm.doc.first_name, frm.doc.middle_name, frm.doc.last_name].filter(Boolean);
	frm.set_value("full_name", parts.join(" "));
}

function show_matches_dialog(frm, matches) {
	let html = `
		<div class="member-matches">
			<p class="text-muted">${__("Found {0} potential matches based on your profile", [matches.length])}</p>
			<div class="matches-list">
	`;

	matches.forEach((match) => {
		let image = match.profile_image || "/assets/frappe/images/default-avatar.png";
		html += `
			<div class="match-card" style="border: 1px solid #d1d8dd; border-radius: 4px; padding: 15px; margin-bottom: 15px;">
				<div style="display: flex; gap: 15px;">
					<img src="${image}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;" />
					<div style="flex: 1;">
						<h5 style="margin: 0 0 5px 0;">
							<a href="/app/member-profile/${match.name}" target="_blank">${match.full_name}</a>
						</h5>
						<p style="margin: 0; color: #6c757d; font-size: 13px;">${match.headline || match.current_position || ""}</p>
						<p style="margin: 5px 0 0 0; color: #6c757d; font-size: 12px;">${match.current_organization || ""}</p>
						<div style="margin-top: 10px;">
							<span class="badge badge-success" style="font-size: 12px;">Match Score: ${match.match_score}%</span>
							${match.willing_to_mentor ? '<span class="badge badge-info" style="font-size: 11px; margin-left: 5px;">Willing to Mentor</span>' : ""}
							${match.open_to_hiring ? '<span class="badge badge-warning" style="font-size: 11px; margin-left: 5px;">Hiring</span>' : ""}
						</div>
					</div>
				</div>
			</div>
		`;
	});

	html += `
			</div>
		</div>
	`;

	frappe.msgprint({
		title: __("Potential Matches"),
		message: html,
		wide: true,
	});
}

function show_member_stats(frm) {
	frappe.call({
		method: "frappe.networking.api.matchmaking.get_member_statistics",
		args: {
			member: frm.doc.name,
		},
		callback: function (r) {
			if (r.message) {
				let stats = r.message;
				let html = `
					<div class="row" style="margin-top: 15px;">
						<div class="col-sm-3">
							<div class="text-center">
								<h3 style="margin: 0; color: #36414c;">${stats.connections || 0}</h3>
								<p class="text-muted" style="margin: 5px 0 0 0; font-size: 12px;">Connections</p>
							</div>
						</div>
						<div class="col-sm-3">
							<div class="text-center">
								<h3 style="margin: 0; color: #36414c;">${stats.meetings || 0}</h3>
								<p class="text-muted" style="margin: 5px 0 0 0; font-size: 12px;">Meetings</p>
							</div>
						</div>
						<div class="col-sm-3">
							<div class="text-center">
								<h3 style="margin: 0; color: #36414c;">${stats.interests || 0}</h3>
								<p class="text-muted" style="margin: 5px 0 0 0; font-size: 12px;">Interests</p>
							</div>
						</div>
						<div class="col-sm-3">
							<div class="text-center">
								<h3 style="margin: 0; color: #36414c;">${stats.skills || 0}</h3>
								<p class="text-muted" style="margin: 5px 0 0 0; font-size: 12px;">Skills</p>
							</div>
						</div>
					</div>
				`;

				frm.dashboard.add_section(html, __("Profile Statistics"));
			}
		},
	});
}
