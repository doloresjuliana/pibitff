// Copyright (c) 2023, DoloresJuliana and contributors
// For license information, please see license.txt

frappe.ui.form.on("TFF Document", {
    refresh(frm) {
       if (!frm.doc.document_text) {
            frm.add_custom_button('Text Capture', () => {
                frappe.call({
                    method: "pibitff.pibitff.doctype.tff_document.tff_document.text_capture",
                    args: { document_name: frm.doc.name,},
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint(__("Text length: {0}", [r.message.text_length]));
                            frm.reload_doc();
                        }
                    },
                });
            })
        }
        if (!frm.doc.recorded_transaction) {
            frm.add_custom_button('Transactional Process', () => {
                frappe.set_route("tff-process", frm.doc.name);
            })
        }
	},
});
