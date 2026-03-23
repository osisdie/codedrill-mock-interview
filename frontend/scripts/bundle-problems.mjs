#!/usr/bin/env node
/**
 * Bundles all problem JSON files into a single file for the demo frontend.
 * Reads backend/data/problems/problem_index.json, loads each problem,
 * and writes frontend/src/demo/problems-bundle.json.
 */
import { readFileSync, writeFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const rootDir = resolve(__dirname, '../..')
const dataDir = resolve(rootDir, 'backend/data/problems')
const outFile = resolve(__dirname, '../src/demo/problems-bundle.json')

const index = JSON.parse(readFileSync(resolve(dataDir, 'problem_index.json'), 'utf-8'))
const problems = []

for (const entry of index.problems) {
  const filePath = resolve(dataDir, entry.file)
  const problem = JSON.parse(readFileSync(filePath, 'utf-8'))
  problems.push(problem)
}

const bundle = { problems }
writeFileSync(outFile, JSON.stringify(bundle))

const sizeKB = (Buffer.byteLength(JSON.stringify(bundle)) / 1024).toFixed(0)
console.log(`Bundled ${problems.length} problems (${sizeKB} KB) → ${outFile}`)
