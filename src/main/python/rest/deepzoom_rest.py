from flask_restful import reqparse, abort, Api, Resource
from io import BytesIO
from flask import current_app,send_file,Response
from pathlib2 import Path

from deepzoom import Deepzoom

api = Api()

IMAGES = {} # ('imageId','full file path')

def abort_if_image_doesnt_exist(imageId):
    if imageId not in IMAGES:
        abort(404, message="Image %s doesn't exist"%(imageId))

parser = reqparse.RequestParser()
parser.add_argument('imageId',default=None)
parser.add_argument('filepath')

class ImageList(Resource):
    def get(self):
        return IMAGES.keys()

    def post(self):
        args = parser.parse_args()
        if args['imageId'] is None:
            if IMAGES.keys()==[]: imageId = 1
            else: imageId = max(map(int,IMAGES.keys()))+1
        else: imageId = args['imageId']
        imageId = str(imageId)
        try:
            p = Path(args['filepath'].strip('"')).resolve()
        except OSError:
            return 'Invalid filepath!', 400
        IMAGES[imageId] = IMAGES.get(imageId,{})
        IMAGES[imageId]['filepath'] = p
        IMAGES[imageId]['dzGen'] = Deepzoom(p,
            create_static_cache=current_app.config.get('DEEPZOOM_REST_STATIC_CACHE',False))
        return imageId, 201

class Image(Resource):
    def get(self, imageId):
        abort_if_image_doesnt_exist(imageId)
        return str(IMAGES[imageId]['filepath'])

    def delete(self, imageId):
        abort_if_image_doesnt_exist(imageId)
        del IMAGES[imageId]
        return '', 204

class Tile(Resource):
    def get(self, imageId, level, col, row, format):
        abort_if_image_doesnt_exist(imageId)
        if format.lower() not in ['jpeg','jpg','png']:
            return 'Invalid image format!',400
        blob = BytesIO()
        IMAGES[imageId]['dzGen'].get_tile(level,col,row).save(blob,format)
        blob.seek(0)
        return send_file(blob, mimetype='image/%s'%format)

class XML(Resource):
    def get(self, imageId):
        abort_if_image_doesnt_exist(imageId)
        xmlStr = IMAGES[imageId]['dzGen'].xml
        resp = Response(xmlStr, mimetype='text/xml')

class JSON(Resource):
    def get(self, imageId):
        abort_if_image_doesnt_exist(imageId)
        xmlStr = IMAGES[imageId]['dzGen'].xml
        resp = Response(xmlStr, mimetype='text/xml')


## Add resources
api.add_resource(ImageList, '/images')
api.add_resource(Image, '/images/<path:imageId>')
api.add_resource(Tile, '/images/<path:imageId>_files/<int:level>/<int:col>_<int:row>.<format>')
api.add_resource(JSON, '/images/<path:imageId>.dzi')
api.add_resource(XML, '/images/<path:imageId>.xml')



if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    api.init_app(app)
    app.run(debug=True)