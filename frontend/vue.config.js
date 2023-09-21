const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})

module.exports = {
  ...module.exports,
  outputDir: 'dist/static',
  assetsDir: './',
  publicPath: '/static/'
}
