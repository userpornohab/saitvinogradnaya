const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  use: { baseURL: 'http://127.0.0.1:8097', trace: 'retain-on-failure' },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } }
  ],
  webServer: {
    command: 'node tests/serve-dist.cjs',
    url: 'http://127.0.0.1:8097',
    reuseExistingServer: false
  }
});
