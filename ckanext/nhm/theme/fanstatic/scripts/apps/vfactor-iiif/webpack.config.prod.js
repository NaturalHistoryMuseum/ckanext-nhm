'use strict';

const {VueLoaderPlugin} = require('vue-loader');

module.exports = {
    mode: 'production',
    entry: [
        './src/app.js'
    ],
    module: {
        rules: [
            {
                test: /\.vue$/,
                use: 'vue-loader'
            },
            {
                test: /\.js$/,
                use: 'babel-loader'
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin()
    ],
    output: {
        library: 'vfactor_iiif',
        libraryTarget: 'umd',
        filename: 'vfactor-iiif.js',
        publicPath: '/fanstatic/scripts/apps/vfactor-iiif/'
    },
    resolve: {
        alias: {
            vue: 'vue/dist/vue.min.js'
        }
    }
};
