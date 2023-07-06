# -*- coding: utf-8 -*-
# Copyright (c) 2021, Midline International WLL
# For license information, please see license.txt

import frappe

from erpnext.stock.doctype.quick_stock_balance.quick_stock_balance import get_stock_item_details


@frappe.whitelist()
def get_item_details(item, customer=None):
    stock = {}
    for warehouse in frappe.db.get_list('Warehouse', filters={'is_group': 0, 'disabled': 0}):
        x = get_stock_item_details(warehouse['name'], None, item, None)
        if x['qty'] > 0:
            stock[warehouse['name']] = x['qty']

    invoice = frappe.db.sql("""
        SELECT
            si.posting_date, sit.parent, sit.item_code, sit.item_name, sit.qty, sit.net_rate, si.status, si.customer_address
        FROM
            `tabSales Invoice Item` AS sit,
            `tabSales Invoice` as si
        WHERE
            sit.parent = si.name AND si.customer = %(customer)s AND
            sit.item_code = %(item)s AND si.docstatus = 1
        ORDER BY
            si.posting_date
        LIMIT 20
    """, values={
        'customer': customer,
        'item': item
    }, as_dict=1)

    for row in invoice:
        row['date'] = frappe.utils.formatdate(row['posting_date'], "dd-mm-yyyy")
        if row['customer_address']:
            row['customer_address'] = str(frappe.db.get_value('Address', row['customer_address'], 'city'))

    order = frappe.db.sql("""
        SELECT
            so.transaction_date, sot.parent, sot.item_code, sot.item_name, sot.qty, sot.net_rate, so.status, so.customer_address
        FROM
            `tabSales Order Item` AS sot,
            `tabSales Order` as so
        WHERE
            sot.parent = so.name AND so.customer = %(customer)s AND
            sot.item_code = %(item)s AND so.docstatus = 1
        ORDER BY
            so.transaction_date
        LIMIT 20
    """, values={
        'customer': customer,
        'item': item
    }, as_dict=1)

    for row in order:
        row['date'] = frappe.utils.formatdate(row['transaction_date'], "dd-mm-yyyy")
        if row['customer_address']:
            row['customer_address'] = str(frappe.db.get_value('Address', row['customer_address'], 'city'))

    quotation = frappe.db.sql("""
        SELECT
            q.transaction_date, qi.parent, qi.item_code, qi.item_name, qi.qty, qi.net_rate, q.status, q.customer_address
        FROM
            `tabQuotation Item` AS qi,
            `tabQuotation` as q
        WHERE
            qi.parent = q.name AND q.party_name = %(customer)s AND
            qi.item_code = %(item)s AND q.docstatus = 1
        ORDER BY
            q.transaction_date
        LIMIT 20
    """, values={
        'customer': customer,
        'item': item
    }, as_dict=1)

    for row in quotation:
        row['date'] = frappe.utils.formatdate(row['transaction_date'], "dd-mm-yyyy")
        if row['customer_address']:
            row['customer_address'] = str(frappe.db.get_value('Address', row['customer_address'], 'city'))

    result = '<div class="row">'
    result += '<div class="col-xs-12 text-center"><b>Sales Invoice</b></div>'
    result += generate_html_table(invoice)
    result += '<div class="col-xs-12 text-center"><b>Sales Order</b></div>'
    result += generate_html_table(order)
    result += '<div class="col-xs-12 text-center"><b>Quotation</b></div>'
    result += generate_html_table(quotation)
    result += '</div>'
    return { 'history': result, 'stock': stock }

def generate_html_table(doc):
    table = """
        <div class="col-xs-12">
            <table class="table table-bordered text-wrap" style="table-layout: fixed;">
                <thead>
                    <tr class="table-info" style="font-weight: bold;">
                        <td style="width:12%;">Date</td>
                        <td style="width:14%;">Document</td>
                        <td style="width:12%;">Item Code</td>
                        <td>Item Name</td>
                        <td style="width:10%;">Qty</td>
                        <td style="width:14%;">Net Rate</td>
                        <td style="width:12%;">Status</td>
                        <td style="width:12%;">City</td>
                    </tr>
                </thead>
                <tbody>
    """
    index = 0
    for row in doc:
        if index >= 5:
            table += '<tr class="table-info item-query-ht hidden">'
        else:
            table += '<tr class="table-info">'
        table += '<td>' + str(row['date']) + '</td>'
        table += '<td>' + str(row['parent']) + '</td>'
        table += '<td>' + str(row['item_code']) + '</td>'
        table += '<td>' + str(row['item_name']) + '</td>'
        table += '<td>' + str(row['qty']) + '</td>'
        table += '<td>' + str(row['net_rate']) + '</td>'
        table += '<td>' + str(row['status']) + '</td>'
        table += '<td>' + str(row['customer_address']) + '</td>'
        table += '</tr>'
        index += 1

    if not len(doc):
        table += """
            <tr class="table-info">
                <td colspan="8" class="text-center">No records found.</td>
            </tr>
        """

    table += """
                </tbody>
            </table>
        </div>
    """
    return table
