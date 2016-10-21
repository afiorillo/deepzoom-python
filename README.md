# Deepzoom (Python)

A DeepZoom suite for Python. Contains facilities to access a generic image as a DeepZoom image, create static DeepZoom image directories, serve DeepZoom images via a RESTful API, and view a DeepZoom image via OpenSeadragon.

## Installation

1. Clone
2. `pip install git+git://github.com/andrewmfiorillo/deepzoom-python`

### TO DOs:
 [ ] Image format plugins (Base class, registration, etc.)
 [ ] Config by file
 [ ] Command-line interface (caching level, config, etc.)
 [ ] RESTful API with Falcon/CherryPy (probably not Flask)
 [ ] Load balancer (each worker has 1 image, many workers)
 [ ] OpenSeadragon or Leaflet page

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## License

MIT License.
