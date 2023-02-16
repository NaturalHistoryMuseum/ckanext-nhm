'use strict';

const { VueLoaderPlugin } = require('vue-loader');

module.exports = {
  mode: 'development',
  entry: ['./src/app.js'],
  module: {
    rules: [
      {
        test: /\.vue$/,
        use: 'vue-loader',
      },
      {
        test: /\.js$/,
        use: 'babel-loader',
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  plugins: [new VueLoaderPlugin()],
  output: {
    library: 'beetle_iiif',
    libraryTarget: 'umd',
    filename: 'beetle-iiif.js',
    publicPath: '/webassets/ckanext-nhm/',
  },
  resolve: {
    alias: {
      vue: 'vue/dist/vue.js',
    },
  },
};
