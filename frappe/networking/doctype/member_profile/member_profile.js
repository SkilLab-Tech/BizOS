frappe.ui.form.on('Member Profile', {
    refresh(frm) {
        frm.add_custom_button('Generate Matches', () => {
            frappe.call({
                method: 'frappe.networking.api.generate_my_matches',
                args: { limit: 5 },
                callback: () => frappe.show_alert({message: 'Matches generated', indicator: 'green'})
            })
        });
    }
});
