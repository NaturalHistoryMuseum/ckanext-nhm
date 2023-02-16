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
      {
        test: /\.(png|jpe?g|gif)$/i,
        loader: 'file-loader',
        options: {
          name: '[name].[ext]',
          publicPath: '/images/leaflet/',
          outputPath: '../../../../../public/images/leaflet',
        },
      },
    ],
  },
  plugins: [new VueLoaderPlugin()],
  output: {
    library: 'search',
    libraryTarget: 'umd',
    filename: 'search.js',
    publicPath: '/webassets/webassets-external/',
  },
  resolve: {
    alias: {
      vue: 'vue/dist/vue.js',
    },
  },
};
