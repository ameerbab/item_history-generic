window.onresize = function() {
    $(".modal-dialog").css( "width", ( $( window ).width() * 0.80 | 0 ) + "px" );
};

// $(document).click(function(event) {
//     if (event.target.className == "btn-click-action") {
//         console.log(event.target.dataset.idx);
//         console.log($('input[data-idx=' + event.target.dataset.idx + ']').val());
//     }
// });

function item_query(frm){
    frm.fields_dict.items.grid.add_custom_button(__('Item Query'), function() {
        let d = new frappe.ui.Dialog({
            title: 'Item Query',
            fields: [
                {
                    label: 'Query Details',
                    fieldname: 'sec_break1',
                    fieldtype: 'Section Break'
                },
                {
                    label: 'Item',
                    fieldname: 'item_code',
                    fieldtype: 'Link',
                    options: 'Item'
                },
                {
                    label: 'Customer',
                    fieldname: 'customer',
                    fieldtype: 'Link',
                    options: 'Customer',
                    default: frm.doc.party_name || frm.doc.customer,
                    read_only: 1
                },
                {
                    fieldname: 'col_break1',
                    fieldtype: 'Column Break'
                },
                {
        			fieldname: 'stock_details',
        			fieldtype: 'Table',
        			label: __('Items'),
        			fields: [
                        {
        					fieldtype: 'Link',
        					fieldname: 'warehouse',
        					label: __('Warehouse'),
        					in_list_view: 1,
                            read_only: 1,
                            options: "Warehouse",
                            onchange: function() {
                                d.fields_dict.stock_details.df.data = [];
                                d.fields_dict.item_code.df.onchange();
                                d.refresh();
        					}
        				},
        				{
        					fieldtype: 'Float',
        					fieldname: 'stock_qty',
        					label: __('Stock Qty'),
        					in_list_view: 1,
                            read_only: 1,
                            onchange: function() {
                                d.fields_dict.stock_details.df.data = [];
                                d.fields_dict.item_code.df.onchange();
                                d.refresh();
        					}
        				},
        				{
        					fieldtype: 'Float',
        					fieldname: 'qty',
        					label: __('Qty'),
        					in_list_view: 1
        				}
        			],
                    data: []
        		},
                {
                    label: 'Item History',
                    fieldname: 'sec_break2',
                    fieldtype: 'Section Break'
                },
                {
                    label: 'History',
                    fieldname: 'inv_history',
                    fieldtype: 'HTML',
                    read_only: 1
                },
            ],
            secondary_action_label: __('Get more data'),
            secondary_action: function() {
                $(".item-query-ht.hidden").each(function(index) {
                   if(index<5) $(this).removeClass('hidden');
                });
            },
            primary_action_label: __('Add Item'),
            primary_action: function() {
                for (const item of d.get_value('stock_details')) {
                    if (item.qty > 0) {
                        var row = frm.add_child('items', {
                            'item_code': d.get_value('item_code'),
                            'qty': item.qty,
                            'warehouse': item.warehouse
                        });
                        frm.script_manager.trigger("item_code", row.doctype, row.name);
                    }
                }
                d.set_value('item_code', '');
            }
        });
        d.fields_dict.item_code.df.onchange = () => {
            if (d.get_value('item_code')) {
                frappe.call({
                    method: "item_history.tasks.get_item_details",
                    args: {
                        item: d.get_value('item_code'),
                        customer: d.get_value('customer')
                    },
                    callback: function(r) {
                        d.fields_dict.inv_history.df.options = r.message.history;
                        d.fields_dict.stock_details.df.data = []
                        Object.keys(r.message.stock).forEach(function(key) {
                            d.fields_dict.stock_details.df.data.push({
                                'warehouse': key,
                                'stock_qty': r.message.stock[key]
                            });
                        });
                        d.refresh();
                    }
                });
            } else {
                d.fields_dict.stock_details.df.data = [];
                d.fields_dict.inv_history.df.options = '';
                d.refresh();
            }
        };
        d.show();
        setTimeout(function () {
            $(".modal-dialog").css( "width", ( $( window ).width() * 0.80 | 0 ) + "px" );
            $(".modal-dialog").css( "maxWidth", ( $( window ).width() * 0.90 | 0 ) + "px" );
        }, 150);
    });
    frm.fields_dict.items.grid.grid_buttons.find('.btn-custom').removeClass('btn-default').addClass('btn-primary');
}

frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
        item_query(frm);
	}
});

frappe.ui.form.on('Sales Order', {
	refresh(frm) {
        item_query(frm);
	}
});

frappe.ui.form.on('Quotation', {
	refresh(frm) {
        item_query(frm);
	}
});
