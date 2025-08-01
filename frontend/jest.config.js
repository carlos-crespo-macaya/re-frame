const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  moduleDirectories: ['node_modules', '<rootDir>/'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-markdown|remark|unified|bail|is-plain-obj|trough|vfile|vfile-message|mdast-util-to-string|micromark|decode-named-character-reference|character-entities|unist-util-visit|unist-util-is|property-information|hast-util-to-jsx-runtime|comma-separated-tokens|hast-util-whitespace|space-separated-tokens|html-url-attributes|mdast-util-to-hast|trim-lines|unist-util-position|unist-util-generated|mdast-util-definitions|ccount|escape-string-regexp|unist-util-visit-parents|remark-parse|mdast-util-from-markdown|mdast-util-to-string|micromark-util-combine-extensions|micromark-util-chunked|micromark-extension-gfm|micromark-util-classify-character|micromark-util-resolve-all|micromark-factory-space|micromark-util-character|micromark-util-symbol|micromark-util-types|micromark-util-encode|micromark-util-sanitize-uri|micromark-core-commonmark|micromark-factory-destination|micromark-factory-label|micromark-factory-title|micromark-factory-whitespace|micromark-util-normalize-identifier|micromark-util-decode-numeric-character-reference|micromark-util-decode-string|micromark-util-subtokenize|micromark-util-html-tag-name|mdast-util-gfm|mdast-util-gfm-autolink-literal|mdast-util-find-and-replace|mdast-util-gfm-footnote|mdast-util-gfm-strikethrough|mdast-util-gfm-table|mdast-util-gfm-task-list-item|remark-gfm|micromark-extension-gfm-autolink-literal|micromark-extension-gfm-footnote|micromark-extension-gfm-strikethrough|micromark-extension-gfm-table|micromark-extension-gfm-task-list-item|micromark-extension-gfm-tagfilter|remark-rehype|unified|trough|bail|is-plain-obj|vfile|vfile-message|unist-util-stringify-position|unist-util-visit|unist-util-is|unist-util-visit-parents|property-information|hast-util-to-jsx-runtime|comma-separated-tokens|hast-util-whitespace|space-separated-tokens|html-url-attributes|unist-util-position|unist-util-generated|trim-lines|style-to-object|inline-style-parser|micromark-util-combine-extensions|micromark-util-chunked|micromark-util-classify-character|micromark-util-resolve-all|micromark-factory-space|micromark-util-character|micromark-util-symbol|micromark-util-types|micromark-core-commonmark|micromark-factory-destination|micromark-factory-label|micromark-factory-title|micromark-factory-whitespace|micromark-util-normalize-identifier|micromark-util-decode-numeric-character-reference|micromark-util-decode-string|micromark-util-subtokenize|micromark-util-html-tag-name|micromark-util-encode|micromark-util-sanitize-uri|ccount|escape-string-regexp|character-entities|decode-named-character-reference|mdast-util-definitions|mdast-util-find-and-replace|devlop|estree-util-is-identifier-name)/)',
  ],
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)