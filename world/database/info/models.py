from __future__ import unicode_literals

import re
from django.db import models
from commands.library import utcnow, sanitize_string, penn_substitutions, ValueError, header, separator, make_table


# Create your models here.


class InfoType(models.Model):
    character_obj = models.ForeignKey('objects.ObjectDB', related_name='infotypes')
    category_name = models.CharField(max_length=30, default='INFO', db_index=True)

    def show_files(self, viewer):
        files = self.files.all()
        message = []
        message.append(header("%s's %s Files" % (self.character_obj.key, self.category_name), viewer=viewer))
        info_table = make_table("Name", "Set On", "Set By", "Approved", width=[20, 29, 19, 9])
        for info in files:
            info_table.add_row(info.title, self.caller.display_local_time(info.date_modified), info.set_by, info.approved)
        message.append(info_table)
        message.append(header(viewer=viewer))
        return "\n".join([unicode(line) for line in message])


class InfoFile(models.Model):
    info_type = models.ForeignKey('info.InfoType', related_name='files')
    title = models.CharField(max_length=30, db_index=True)
    date_created = models.DateTimeField(default=utcnow())
    date_modified = models.DateTimeField(default=utcnow())
    text = models.TextField()
    set_by = models.ForeignKey('communications.ObjectStub', null=True, on_delete=models.SET_NULL)
    date_approved = models.DateTimeField(null=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('communications.ObjectStub',null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.title
    
    def __len__(self):
        return len(self.text)
    
    def set_approved(self, approver=None):
        if not approver:
            raise ValueError("Approver is not defined.")
        if self.approved:
            raise ValueError("File '%s' is already approved." % self.title)
        self.approved = True
        self.approved_by = approver
        self.date_approved = utcnow()
        self.save()
        self.character_obj.sys_msg("File '%s' is now approved." % self.title, sys_name=self.info_category)

    def set_unapproved(self):
        if not self.approved:
            raise ValueError("File '%s' is not approved." % self.title)
        self.approved = False
        self.approved_by = None
        self.date_approved = None
        self.save()
        self.character_obj.sys_msg("File '%s' is no longer approved." % self.title, sys_name=self.info_category)

    def set_name(self, newname=None):
        oldname = self.title
        newname = valid_name(newname)
        if self.character_obj.infofiles.filter(title__iexact=newname,
                                               info_category=self.info_category).exclude(id=self.id):
            raise ValueError("That name conflicts with an existing Info file.")
        self.title = newname
        self.save()
        self.character_obj.sys_msg("File '%s' renamed to '%s'!" % (oldname, self.title),
                                   sys_name=self.info_category)
        
    def set_contents(self, newtext=None, setby=None):
        if not setby:
            raise ValueError("File setter data not found.")
        if not newtext:
            raise ValueError("No text entered to set!")
        if self.approved:
            raise ValueError("Cannot edit an approved file.")
        self.text = penn_substitutions(newtext)
        self.set_by = setby
        self.date_modified = utcnow()
        self.save()
        self.character_obj.sys_msg("File '%s' has been updated." % self.title, sys_name=self.info_category)

    def del_file(self):
        if self.approved:
            raise ValueError("Cannot delete an approved file.")
        self.character_obj.sys_msg("File '%s' deleted." % self.title, sys_name=self.info_category)
        self.delete()

    def show_info(self, viewer):
        message = []
        message.append(header("%s's %s File: %s" % (self.info_type.character_obj, self.info_type.category_name,
                                                    self.title)))
        message.append(self.text)
        message.append(separator())
        message.append("{wLast set by:{n %s {wOn:{n %s" % (self.set_by,
                                                           viewer.display_local_time(date=self.date_modified)))
        if self.approved:
            message.append("{wApproved by:{n %s {wOn:{n %s" % (self.approved_by,
                                                               viewer.display_local_time(self.date_approved)))
        message.append(header())
        return "\n".join([unicode(line) for line in message])

def valid_name(namecheck=None):
    if not namecheck:
        raise ValueError("Name field empty.")
    namecheck = sanitize_string(namecheck, strip_ansi=True)
    if not re.match('^[\w-]+$', namecheck):
        raise ValueError("File '%s' could not be set: Info names must be alphanumeric." % namecheck)
    if len(namecheck) > 18:
        raise ValueError("Info File names may not exceed 18 characters.")
    return namecheck