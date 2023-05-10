import { createApp, watchEffect } from "vue";
import { createPinia } from "pinia";
//import { useStore } from "./store";
import TffProcessComponent from "./components/TffProcess.vue";
import { registerGlobalComponents } from "./globals.js";

class TffProcess {
	constructor({ wrapper, page, docname }) {
		this.$wrapper = $(wrapper);
		this.page = page;
		this.docname = docname;
		this.read_only = false;
		this.get_document();
		this.get_doctype_transaction();
		this.doctype_url = this.doctype_transaction.toLowerCase().replace(" ", "-");
		this.site_path = this.get_base_url();
		this.urlpdf = this.site_path + this.document.document_pdf;
		if (!this.document.recorded_transaction){
			this.urldoctype = this.site_path + "/app/" + 
			this.doctype_url + "/new";
		} else {
			this.urldoctype = this.site_path + "/app/" + 
			this.doctype_url + "/" + this.document.name_transaction;
		}
	
		this.init();
	}

	init(refresh) {
		// set page title
		this.page.set_title(__("Transactional Process: {0}", [this.document.name]));
		this.setup_page_actions();
		!refresh && this.setup_app();
		//this.watch_changes();
	}

	async setup_page_actions() {
		// clear actions
		this.page.clear_actions();
		this.page.clear_menu();
		this.page.clear_custom_actions();

		// setup page actions
		this.primary_btn = this.page.set_primary_action(__("Save"), () =>
			this.store.save_changes()
		);
	}

	setup_app() {
		// create a pinia instance
		let pinia = createPinia();

		// create a vue instance
		let app = createApp(TffProcessComponent, {
			urlpdf: this.urlpdf,
      		urldoctype: this.urldoctype
		});
		SetVueGlobals(app);
		app.use(pinia);

		// create a store
		//this.store = useStore();
		//this.store.doctype = this.doctype;
		//this.store.is_customize_form = this.customize;
		//this.store.page = this.page;

		// register global components
		registerGlobalComponents(app);

		// mount the app
		this.$tff_process = app.mount(this.$wrapper.get(0));
	}

	watch_changes() {
		watchEffect(() => {
			if (this.store.dirty) {
				this.page.set_indicator(__("Not Saved"), "orange");
				this.reset_changes_btn.show();
			} else {
				this.page.clear_indicator();
				this.reset_changes_btn.hide();
			}

			// toggle doctype / customize form btn based on url
			this.customize_form_btn.toggle(!this.store.is_customize_form);
			this.doctype_form_btn.toggle(this.store.is_customize_form);

			// hide customize form & Go to customize form btn
			if (
				this.store.doc &&
				(this.store.doc.custom ||
					this.store.doc.issingle ||
					in_list(frappe.model.core_doctypes_list, this.doctype))
			) {
				this.customize_form_btn.hide();
				if (this.doctype != "Customize Form") {
					this.go_to_customize_form_btn.hide();
				}
			}

			// show Go to {0} List or Go to {0} button
			if (this.store.doc && !this.store.doc.istable) {
				let label = this.store.doc.issingle
					? __("Go to {0}", [__(this.doctype)])
					: __("Go to {0} List", [__(this.doctype)]);

				this.go_to_doctype_list_btn.text(label);
			}

			// toggle preview btn text
			this.preview_btn.text(this.store.preview ? __("Hide Preview") : __("Show Preview"));

			// toggle primary btn and show indicator based on read_only state
			this.primary_btn.toggle(!this.store.read_only);
			if (this.store.read_only) {
				let message = this.store.preview ? __("Preview Mode") : __("Read Only");
				this.page.set_indicator(message, "orange");
			}
		});
	}

	get_document() {
		var me = this;
		frappe.call({
			method: "pibitff.pibitff.doctype.tff_document.tff_document.get_document",
			args: { document_name: this.docname, },
			async: false,
			callback: function (r) {
				if (r.message) {
					me.document = r.message;
				}
			},
		});
	}

	get_doctype_transaction() {
		if (this.document.recorded_transaction && this.document.doctype_transaction ) {
			this.doctype_transaction = this.document.doctype_transaction;
		} else {
			var me = this;
			frappe.call({
				method: "pibitff.pibitff.doctype.tff_document.tff_document.get_doctype",
				args: { document_classification: this.document.document_classification, },
				async: false,
				callback: function (r) {
					if (r.message) {
						me.doctype_transaction = r.message;
					}
				},
			});
		}
	}

	get_base_url() {
		// var url= (frappe.base_url || window.location.href).split('#')[0].split('?')[0].split('desk')[0];
		var url = frappe.base_url || window.location.origin;
		if (url.substr(url.length - 1, 1) == "/") url = url.substr(0, url.length - 1);
		return url;
	}
}

frappe.provide("frappe.ui");
frappe.ui.TffProcess = TffProcess;
export default TffProcess;