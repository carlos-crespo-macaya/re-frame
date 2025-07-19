# Voice Modality CI/CD Documentation

## Overview

This document describes the CI/CD pipeline for the voice modality feature in the CBT Assistant POC. The pipeline ensures comprehensive testing and quality checks for all voice-related functionality.

## CI/CD Pipeline Structure

### 1. Voice Unit Tests (`voice-tests.yml`)

**Trigger**: On push to voice-related files or pull requests
**Purpose**: Run unit tests for voice components

#### Jobs:
- **voice-unit-tests**: Tests backend audio processing and frontend voice components
  - Installs audio processing dependencies (ffmpeg, sox, libasound2-dev)
  - Runs backend voice tests with coverage reporting
  - Runs frontend voice-related tests

**Key Features**:
- Audio codec support via system dependencies
- Coverage reporting for voice modules
- Parallel execution of backend and frontend tests

### 2. Voice E2E Tests (`voice-playwright-tests.yml`)

**Trigger**: After voice unit tests pass
**Purpose**: End-to-end testing of voice features across browsers

#### Jobs:
- **voice-e2e-tests**: Tests voice functionality in real browsers
  - Matrix testing across Chromium, Firefox, and WebKit
  - Audio input simulation
  - Network resilience testing
  - Session isolation verification

**Key Features**:
- Multi-browser support
- Artifact upload for test results
- Parallel browser testing

### 3. Voice Load Tests (`voice-load-tests.yml`)

**Trigger**: On push to main branch only
**Purpose**: Performance and load testing

#### Jobs:
- **voice-performance-tests**: Runs load tests and analyzes performance
  - 50 concurrent user simulation
  - Sustained load testing
  - Performance metric analysis
  - Automated performance reports

**Key Features**:
- k6 load testing integration
- Performance threshold validation
- PR commenting with results

## Environment Variables

### Required Secrets
```yaml
GEMINI_API_KEY: # Google AI API key for STT/TTS services
```

### Configuration Variables
```yaml
VOICE_MODE_ENABLED: true          # Enable voice processing
AUDIO_MAX_SIZE_MB: 10            # Maximum audio file size
CONCURRENT_USERS: 50             # Load test concurrent users
TEST_DURATION: 60                # Load test duration in seconds
```

## Local Development

### Running Tests Locally

#### Unit Tests
```bash
# Backend voice tests
cd backend
uv run pytest tests/test_audio* -v

# Frontend voice tests
cd frontend
pnpm test -- --testNamePattern="voice|audio"
```

#### Integration Tests
```bash
# Using Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.integration.yml up
```

#### Load Tests
```bash
# With k6 installed
k6 run tests/load/k6/voice-load-test.js

# Using Docker
docker-compose -f docker-compose.yml -f docker-compose.perf.yml up
```

### Performance Monitoring

Access monitoring dashboards:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

## CI/CD Workflows

### Pre-merge Checks
1. Code formatting (black, prettier)
2. Linting (ruff, eslint)
3. Type checking (mypy, typescript)
4. Unit tests with coverage
5. Integration tests
6. E2E tests (sample)

### Post-merge Actions
1. Full E2E test suite
2. Load testing
3. Performance analysis
4. Metric collection

## Performance Thresholds

The pipeline enforces these performance requirements:

| Metric | Threshold | Description |
|--------|-----------|-------------|
| Error Rate | < 1% | Overall request error rate |
| P95 Response Time | < 2s | 95th percentile response time |
| P99 Response Time | < 5s | 99th percentile response time |
| Throughput | > 10 req/s | Minimum sustained throughput |
| Audio Processing | < 3s | P95 audio request latency |

## Troubleshooting

### Common Issues

#### 1. Audio Dependencies Missing
```bash
# Install on Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg sox libasound2-dev

# Install on macOS
brew install ffmpeg sox
```

#### 2. Voice Mode Not Enabled
Ensure `VOICE_MODE_ENABLED=true` is set in environment

#### 3. Performance Test Failures
Check:
- Service resource limits
- Network latency
- External API rate limits

### Debugging Commands

```bash
# Check service health
./scripts/wait-for-services.sh

# View performance metrics
./scripts/analyze_performance.py

# Check Docker logs
docker-compose logs backend frontend
```

## Best Practices

### 1. Test Data Management
- Use synthetic audio samples for tests
- Never commit real user audio data
- Generate test audio programmatically

### 2. Performance Testing
- Run load tests during off-peak hours
- Monitor external API usage
- Set realistic performance targets

### 3. Security
- Audio data is never logged
- Use mock services for sensitive tests
- Validate all audio inputs

## Maintenance

### Weekly Tasks
- Review performance trends
- Update test baselines
- Check dependency updates

### Monthly Tasks
- Full load test run
- Performance report generation
- Security audit of audio handling

## Integration with Main CI/CD

The voice modality tests integrate with the main monorepo CI/CD:

1. **ci-monorepo.yml** includes voice test jobs
2. **pr-validation.yml** runs voice checks
3. **release.yml** includes voice performance validation

## Future Enhancements

1. **WebRTC Support**: Real-time audio streaming tests
2. **Multi-language Testing**: Automated tests for all supported languages
3. **Chaos Engineering**: Network failure simulation
4. **A/B Testing**: Performance comparison framework

## References

- [Voice Modality Testing Strategy](./VOICE_MODALITY_TESTING_STRATEGY.md)
- [E2E Testing Guide](./E2E_TESTING_GUIDE.md)
- [Performance Monitoring](../backend/src/utils/performance_monitor.py)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)