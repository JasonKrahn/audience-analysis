## Usage

 * copy template.config.yaml to config.yaml and add some secrets
 * note it assumes you have event hub, stream analytics and power bi
    * automatic creation from template is on the roadmap
 * to use localy, just use `python util.py run_docker`
 * to run as a web app, run `python util.py create_app [-d|--dry]`
 * to feed an image to backend, test with feed_image.cmd (no shell version at this moment)