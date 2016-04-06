module.exports = function(grunt) {
    
    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        jshint: {
            files: ['gruntfile.js', 'index.js', 'js/**/*.js'],
            options: {
                // options here to override JSHint defaults
                globals: {
                    console: true,
                    module: true,
                    document: true
                }
            }
        },
        browserify: {
            '../static/js/App.js': ['index.js']
        },
        handlebars: {
            compile: {
                options: {
                    node: true,
                    namespace: 'Templates',
                    partialsUseNamespace: true,
                    processName: function(filePath) {
                        var file = filePath.replace(/.*\/(\w+)\.hbs/, '$1');
                        return file;
                    }
                },
                files:{
                    'js/templates.js': ['templates/*.hbs']
                }
            }
        },
        stylus: {
            '../static/css/App.css': ['styl/*.styl'], // compile and concat into single file
            options: {
                urlfunc: {
                    name:'embedurl',
                    limit:false
                },
                'include css':true
            }
        },
        processhtml: {
           dist: {
               files: {
                   '../templates/index.html': ['html/index.html']
               }
           }
        },
        uglify: {
            my_target: {
                files: {
                    '../static/js/App.min.js': ['../static/js/App.js']
                }
            }
        },
        watch: {
            scripts: {
                files: ['index.js', 'styl/*.styl', 'templates/*.hbs'],
                tasks: ['dist']
            },
        }
    });
    
    //Tasks
    grunt.registerTask('dist', ['jshint', 'handlebars', 'stylus', 'browserify', 'processhtml', 'uglify']);
    
    // Load the plugins
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-contrib-stylus');
    grunt.loadNpmTasks('grunt-processhtml');
    grunt.loadNpmTasks('grunt-contrib-handlebars');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    
    /*grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-contrib-handlebars');
    grunt.loadNpmTasks('grunt-contrib-stylus');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-simple-mocha');
    grunt.loadNpmTasks('grunt-contrib-uglify');*/
    
};