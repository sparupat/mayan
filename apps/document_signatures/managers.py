import logging

from django.db import models

from django_gpg.runtime import gpg
from django_gpg.exceptions import GPGVerificationError

logger = logging.getLogger(__name__)


class DocumentVersionSignatureManager(models.Manager):
    #def update_signed_state(self, document):
    #    document_signature, created = self.model.get_or_create(
    #        document_version=document.latest_version,
    #    )
    #    if document.exists():
    #        descriptor = document.open()
    #        try:
    #            document_signature.signature_state = gpg.verify_file(descriptor).status
    #            # TODO: give use choice for auto public key fetch?
    #            # OR maybe new config option
    #        except GPGVerificationError:
    #            document_signature.signature_state = None
    #        finally:
    #            document_signature.save()

    def add_detached_signature(self, document, detached_signature):
        document_signature, created = self.model.objects.get_or_create(
            document_version=document.latest_version,
        )
        if not self.signature_state(document):
            document_signature.signature_file = detached_signature
            document_signature.save()
        else:
            raise Exception('document already has an embedded signature')

    def has_detached_signature(self, document):
        document_signature, created = self.model.objects.get_or_create(
            document_version=document.latest_version,
        )
        if document_signature.signature_file:
            return True
        else:
            return False

    def has_embedded_signature(self, document):
        logger.debug('document: %s' % document)

        if self.signature_state(document):
            return True
        else:
            return False

    def signature_state(self, document):
        document_signature, created = self.model.objects.get_or_create(
            document_version=document.latest_version,
        )
        logger.debug('created: %s' % created)
        if created and document.exists():
            descriptor = document.open(raw=True)
            try:
                document_signature.signature_state = gpg.verify_file(descriptor).status
                # TODO: give use choice for auto public key fetch?
                # OR maybe new config option
            except GPGVerificationError:
                document_signature.signature_state = None
            finally:
                document_signature.save()

            #document_signature.signature_state = self.verify_signature(document).status
            #document_signature.save()

        return document_signature.signature_state

    def detached_signature(self, document):
        document_signature, created = self.model.objects.get_or_create(
            document_version=document.latest_version,
        )
        return document_signature.signature_file.storage.open(document_signature.signature_file.path)

    def verify_signature(self, document):
        if self.has_detached_signature(document):
            logger.debug('has detached signature')
            args = (document.open(raw=True), self.detached_signature(document))
        else:
            args = (document.open(raw=True),)

        try:
            return gpg.verify_w_retry(*args)
        except GPGVerificationError:
            return None