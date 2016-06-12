import datetime
from peewee import *

DBVERSION = 1
try:
    DATABASE
except NameError:
    DATABASE = 'imagine.db' # default value

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'cr2']
IMAGE_EXTENSIONS_RAW = ['cr2']

#try:
#    database
#except NameError:
#    database = SqliteDatabase(DATABASE)
database = None


# == imagine models

class BaseModel(Model):
    class Meta:
        database = database


class Collection(BaseModel):
    """Collection of images in a certain base_dir"""
    name = CharField()
    slug = CharField(null=True)
    base_dir = CharField()

    added_at = DateTimeField(default=datetime.datetime.now())

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.base_dir)


class Directory(BaseModel):
    """Directory/collection umbrella object"""
    directory = CharField()
    collection = ForeignKeyField(Collection)

    added_at = DateTimeField(default=datetime.datetime.now())

    def get_filepath(self, filename):
        return '{0}{1}'.format(self.directory, filename)

    def __unicode__(self):
        return self.directory


class Image(BaseModel):
    """Image object, with generic image file information"""
    directory = ForeignKeyField(Directory, related_name='parent')
    filename = CharField()
    file_ext = CharField()
    filetype = CharField(null=True)
    filesize = IntegerField(default=-1)
    file_modified = DateTimeField(null=True)

    added_at = DateTimeField(default=datetime.datetime.now())
    title = TextField(default='')
    description = TextField(default='')
    is_visible = BooleanField(default=True)

    width = IntegerField(default=-1)
    height = IntegerField(default=-1)

    image_hash = CharField(null=True)
    thumb_hash = CharField(null=True)

    class Meta:
        order_by = ('filename',)


    def get_filepath(self):
        return '{0}{1}'.format(self.directory.directory, self.filename)


    def get_similar(self):
        return Image.select().where(Image.image_hash==self.image_hash)


    def __unicode__(self):
        return self.get_filepath()


class ExifItem(BaseModel):
    """Piece of exif info of a certain Image"""
    image = ForeignKeyField(Image)
    key = CharField()
    value_str = CharField(null=True)
    value_int = IntegerField(null=True)
    value_float = FloatField(null=True)

    def get_value(as_type='str'):
        if value_str:
            return value_str
        elif value_int:
            return value_int
        elif value_float:
            return value_float
        else:
            return None


# the user model specifies its fields (or columns) declaratively, like django
class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField()
    join_date = DateTimeField()

    class Meta:
        order_by = ('username',)


def create_archive():
    database.connect()
    Collection.create_table()
    Directory.create_table()
    Image.create_table()
    ExifItem.create_table()
    User.create_table()


def is_image(filename):
    f = filename.lower()
    for ext in IMAGE_EXTENSIONS:
        if f.endswith(ext):
            return True
    return False

