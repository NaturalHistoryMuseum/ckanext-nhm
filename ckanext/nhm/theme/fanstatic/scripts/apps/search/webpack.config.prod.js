'use strict';

const {VueLoaderPlugin} = require('vue-loader');

module.exports = {
    mode:    'production',
    entry:   [
        './src/app.js'
    ],
    module:  {
        rules: [
            {
                test: /\.vue$/,
                use:  'vue-loader'
            },
            {
                test: /\.js$/,
                use:  'babel-loader'
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.(png|jpe?g|gif)$/i,
                use:  'file-loader'
            },
        ]
    },
    plugins: [
        new VueLoaderPlugin()
    ],
    output:  {
        library:       'search',
        libraryTarget: 'umd',
        filename:      'search.js'
    },
    resolve: {
        alias: {
            vue: 'vue/dist/vue.js'
        }
    }
};