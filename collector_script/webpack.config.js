const path = require('path');

module.exports = {
  entry: './index.js',
  output: {
    path: path.resolve(__dirname, '../client/public/static'),
    filename: 'collector.min.js',
  },
};
