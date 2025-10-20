// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
// License: MIT. See LICENSE

frappe.ui.form.on('Profile', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Find Matches'), function() {
                frappe.route_options = {
                    "profile": frm.doc.name
                };
                frappe.set_route("List", "Profile");
            });
            
            frm.add_custom_button(__('Send Meeting Request'), function() {
                frappe.route_options = {
                    "from_profile": frm.doc.name
                };
                frappe.set_route("List", "Meeting Request");
            });
            
            frm.add_custom_button(__('View Analytics'), function() {
                frappe.route_options = {
                    "profile": frm.doc.name
                };
                frappe.set_route("Report", "Profile Analytics");
            });
        }
        
        // Set user details when user is selected
        if (frm.doc.user) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "User",
                    name: frm.doc.user
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("full_name", r.message.full_name);
                        frm.set_value("email", r.message.email);
                        frm.set_value("phone", r.message.phone);
                        frm.set_value("profile_image", r.message.user_image);
                    }
                }
            });
        }
    },
    
    user: function(frm) {
        if (frm.doc.user) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "User",
                    name: frm.doc.user
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("full_name", r.message.full_name);
                        frm.set_value("email", r.message.email);
                        frm.set_value("phone", r.message.phone);
                        frm.set_value("profile_image", r.message.user_image);
                    }
                }
            });
        }
    },
    
    can_mentor: function(frm) {
        if (frm.doc.can_mentor && !frm.doc.mentorship_area) {
            frappe.msgprint(__("Please specify the mentorship area in the Professional Information section"));
        }
    },
    
    seeking_mentor: function(frm) {
        if (frm.doc.seeking_mentor && !frm.doc.goals) {
            frappe.msgprint(__("Please specify your goals in the Mentorship section"));
        }
    }
});

// Custom functions
frappe.ui.form.on('Profile', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Get AI Suggestions'), function() {
                get_ai_suggestions(frm);
            });
            
            frm.add_custom_button(__('View Networking Stats'), function() {
                show_networking_stats(frm);
            });
        }
    }
});

function get_ai_suggestions(frm) {
    frappe.call({
        method: "nonprofit_networking.ai.matchmaking.get_ai_suggestions",
        args: {
            profile: frm.doc.name,
            limit: 5
        },
        callback: function(r) {
            if (r.message) {
                show_ai_suggestions(r.message);
            }
        }
    });
}

function show_ai_suggestions(suggestions) {
    let html = '<div class="ai-suggestions">';
    html += '<h4>AI-Powered Suggestions</h4>';
    
    suggestions.forEach(function(suggestion) {
        html += '<div class="suggestion-item">';
        html += '<h5>' + suggestion.profile_name + '</h5>';
        html += '<p><strong>Match Score:</strong> ' + suggestion.match_score + '%</p>';
        html += '<p><strong>Purpose:</strong> ' + suggestion.purpose + '</p>';
        html += '<p><strong>Reason:</strong> ' + suggestion.reason + '</p>';
        html += '<p><strong>Message:</strong> ' + suggestion.message + '</p>';
        html += '</div>';
    });
    
    html += '</div>';
    
    let d = new frappe.ui.Dialog({
        title: __('AI Suggestions'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'suggestions_html',
                options: html
            }
        ],
        size: 'large'
    });
    
    d.show();
}

function show_networking_stats(frm) {
    frappe.call({
        method: "nonprofit_networking.profile.get_networking_stats",
        args: {
            profile: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                let stats = r.message;
                let html = '<div class="networking-stats">';
                html += '<h4>Networking Statistics</h4>';
                html += '<div class="stats-grid">';
                html += '<div class="stat-item"><strong>Total Meetings:</strong> ' + stats.total_meetings + '</div>';
                html += '<div class="stat-item"><strong>Mentorships:</strong> ' + stats.total_mentorships + '</div>';
                html += '<div class="stat-item"><strong>Connections:</strong> ' + stats.total_connections + '</div>';
                html += '<div class="stat-item"><strong>Profile Views:</strong> ' + stats.profile_views + '</div>';
                html += '</div>';
                html += '</div>';
                
                let d = new frappe.ui.Dialog({
                    title: __('Networking Statistics'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'stats_html',
                            options: html
                        }
                    ],
                    size: 'medium'
                });
                
                d.show();
            }
        }
    });
}