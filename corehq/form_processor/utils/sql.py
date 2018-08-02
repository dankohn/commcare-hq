"""
Note that the adapters must return the fields in the same order as they appear
in the table DSL
"""
from __future__ import absolute_import
from __future__ import unicode_literals
import json
from collections import namedtuple

from jsonfield.fields import JSONEncoder
from psycopg2.extensions import adapt

from corehq.form_processor.models import (
    CommCareCaseSQL_DB_TABLE, CaseAttachmentSQL_DB_TABLE,
    CommCareCaseIndexSQL_DB_TABLE, CaseTransaction_DB_TABLE,
    XFormAttachmentSQL_DB_TABLE, XFormInstanceSQL_DB_TABLE,
    LedgerValue_DB_TABLE, LedgerTransaction_DB_TABLE,
    XFormOperationSQL_DB_TABLE,
)


def fetchall_as_namedtuple(cursor):
    "Return all rows from a cursor as a namedtuple generator"
    Result = _namedtuple_from_cursor(cursor)
    return (Result(*row) for row in cursor)


def fetchone_as_namedtuple(cursor):
    "Return one row from a cursor as a namedtuple"
    Result = _namedtuple_from_cursor(cursor)
    row = cursor.fetchone()
    return Result(*row)


def _namedtuple_from_cursor(cursor):
    desc = cursor.description
    return namedtuple('Result', [col[0] for col in desc])


def form_adapter(form):
    fields = [
        form.id,
        form.form_id,
        form.domain,
        form.app_id,
        form.xmlns,
        form.received_on,
        form.partial_submission,
        form.submit_ip,
        form.last_sync_token,
        form.date_header,
        form.build_id,
        form.state,
        json.dumps(form.auth_context, cls=JSONEncoder),
        json.dumps(form.openrosa_headers, cls=JSONEncoder),
        form.deprecated_form_id,
        form.edited_on,
        form.orig_id,
        form.problem,
        form.user_id,
        form.initial_processing_complete,
        form.deleted_on,
        form.deletion_id,
        form.server_modified_on,
    ]
    return ObjectAdapter(fields, XFormInstanceSQL_DB_TABLE)


def form_attachment_adapter(attachment):
    fields = [
        attachment.id,
        attachment.attachment_id,
        attachment.name,
        attachment.content_type,
        attachment.md5,
        attachment.form_id,
        attachment.blob_id,
        attachment.content_length,
        json.dumps(attachment.properties, cls=JSONEncoder),
        attachment.blob_bucket,
    ]
    return ObjectAdapter(fields, XFormAttachmentSQL_DB_TABLE)


def form_operation_adapter(operation):
    fields = [
        operation.id,
        operation.user_id,
        operation.operation,
        operation.date,
        operation.form_id,
    ]
    return ObjectAdapter(fields, XFormOperationSQL_DB_TABLE)


def case_adapter(case):
    fields = [
        case.id,
        case.case_id,
        case.domain,
        case.type,
        case.owner_id,
        case.opened_on,
        case.opened_by,
        case.modified_on,
        case.server_modified_on,
        case.modified_by,
        case.closed,
        case.closed_on,
        case.closed_by,
        case.deleted,
        case.external_id,
        json.dumps(case.case_json, cls=JSONEncoder),
        case.name,
        case.location_id,
        case.deleted_on,
        case.deletion_id,
    ]
    return ObjectAdapter(fields, CommCareCaseSQL_DB_TABLE)


def case_attachment_adapter(attachment):
    fields = [
        attachment.id,
        attachment.attachment_id,
        attachment.name,
        attachment.content_type,
        attachment.md5,
        attachment.case_id,
        attachment.blob_id,
        attachment.content_length,
        json.dumps(attachment.properties, cls=JSONEncoder),
        attachment.blob_bucket,
    ]
    return ObjectAdapter(fields, CaseAttachmentSQL_DB_TABLE)


def case_index_adapter(index):
    fields = [
        index.id,
        index.domain,
        index.identifier,
        index.referenced_id,
        index.referenced_type,
        index.relationship_id,
        index.case_id,
    ]
    return ObjectAdapter(fields, CommCareCaseIndexSQL_DB_TABLE)


def case_transaction_adapter(transaction):
    fields = [
        transaction.id,
        transaction.form_id,
        transaction.server_date,
        transaction.client_date,
        transaction.type,
        transaction.case_id,
        transaction.revoked,
        json.dumps(transaction.details, cls=JSONEncoder),
        transaction.sync_log_id,
    ]
    return ObjectAdapter(fields, CaseTransaction_DB_TABLE)


def ledger_value_adapter(ledger_value):
    fields = [
        ledger_value.id,
        ledger_value.entry_id,
        ledger_value.section_id,
        ledger_value.balance,
        ledger_value.last_modified,
        ledger_value.case_id,
        ledger_value.daily_consumption,
        ledger_value.last_modified_form_id,
        ledger_value.domain,
    ]
    return ObjectAdapter(fields, LedgerValue_DB_TABLE)


def ledger_transaction_adapter(ledger_transaction):
    fields = [
        ledger_transaction.id,
        ledger_transaction.form_id,
        ledger_transaction.server_date,
        ledger_transaction.report_date,
        ledger_transaction.type,
        ledger_transaction.case_id,
        ledger_transaction.entry_id,
        ledger_transaction.section_id,
        ledger_transaction.user_defined_type,
        ledger_transaction.delta,
        ledger_transaction.updated_balance,
    ]
    return ObjectAdapter(fields, LedgerTransaction_DB_TABLE)


class ObjectAdapter(object):
    def __init__(self, fields, table_name):
        self.table_name = table_name
        self.fields = [
            adapt(field) for field in fields
        ]

    def getquoted(self):
        fields = [field.getquoted() for field in self.fields]
        params = ['{}'] * len(fields)
        template = "ROW({})::{}".format(','.join(params), self.table_name)
        return template.format(*fields)

    def prepare(self, conn):
        for field in self.fields:
            if hasattr(field, 'prepare'):
                field.prepare(conn)


def get_case_transactions_by_case_id(case_id, updated_xforms=None):
    """
    This fetches all the transactions required to rebuild the case along
    with all the forms for those transactions.

    For any forms that have been updated it replaces the old form
    with the new one.

    :param case_id: ID of case to rebuild
    :param updated_xforms: list of forms that have been changed.
    :return: list of ``CaseTransaction`` objects with their associated forms attached.
    """

    transactions = CaseAccessorSQL.get_transactions_for_case_rebuild(case_id)
    return fetch_case_transaction_forms(transactions, updated_xforms)


def fetch_case_transaction_forms(transactions, updated_xforms=None):
    """
    Fetches the forms for a list of transactions

    :param transactions: list of ``CaseTransaction`` objects:
    :param updated_xforms: list of forms that have been changed.
    :return: list of ``CaseTransaction`` objects with their associated forms attached.
    """

    form_ids = {tx.form_id for tx in transactions}
    updated_xforms_map = {
        xform.form_id: xform for xform in updated_xforms if not xform.is_deprecated
    } if updated_xforms else {}

    form_ids_to_fetch = list(form_ids - set(updated_xforms_map.keys()))
    xform_map = {form.form_id: form for form in FormAccessorSQL.get_forms_with_attachments_meta(form_ids_to_fetch)}

    def get_form(form_id):
        if form_id in updated_xforms_map:
            return updated_xforms_map[form_id]

        try:
            return xform_map[form_id]
        except KeyError:
            raise XFormNotFound

    for transaction in transactions:
        if transaction.form_id:
            try:
                transaction.cached_form = get_form(transaction.form_id)
            except XFormNotFound:
                logging.error('Form not found during rebuild: %s', transaction.form_id)

    return transactions
