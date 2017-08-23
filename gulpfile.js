var gulp = require('gulp');
var notify = require('gulp-notify');
var less = require('gulp-less');

var themeDir = 'ckanext/nhm/theme';

// Sass file location
var lessSrcDir = themeDir + '/less';

// Directory LESS should compile to?
var lessTargetDir = themeDir + '/fanstatic/css';

// Compile less & save to target CSS directory
gulp.task('css', function () {
    return gulp.src(lessSrcDir + '/*.less')
        .pipe(less())
        .pipe(gulp.dest(lessTargetDir))
        .pipe(notify('CSS minified'))
});

// Watch less src for changes
gulp.task('watch', function () {
    gulp.watch(lessSrcDir + '/*.less', ['css']);
});

// What tasks does running gulp trigger?
gulp.task('default', ['css', 'watch']);