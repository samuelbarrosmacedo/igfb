import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["json", { outputFile: "test-results/results.json" }]],
  use: {
    baseURL: process.env.IGFB_TEST_URL || "http://127.0.0.1:4173/igfb/",
    trace: "retain-on-failure",
    launchOptions: process.env.IGFB_CHROMIUM_PATH
      ? { executablePath: process.env.IGFB_CHROMIUM_PATH }
      : {},
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"], isMobile: true } },
  ],
  webServer:
    process.env.SITES_MANAGED_LINUX_CONTAINER === "1"
      ? undefined
      : {
          command: "npm run preview -- --port 4173",
          url: "http://127.0.0.1:4173/igfb/",
          reuseExistingServer: !process.env.CI,
        },
});
