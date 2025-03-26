# Docker Usage Guide for Texas Holdem Win Rate Calculator

This guide provides detailed instructions on how to use the Texas Holdem Win Rate Calculator with Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- For GPU support (optional): [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

## Basic Usage

### Building and Running the Tests

The default Docker Compose configuration will build the application and run the test suite:

```bash
docker-compose up
```

This will output the test results for the predefined test cases and save the results to `data/test_result.json`.

### Interactive Mode

To run the calculator in interactive mode:

```bash
docker-compose run poker-interactive
```

This will open a bash shell inside the container where you can run Python scripts:

```bash
# Inside the container
python calculator.py
```

### Custom Calculations

To run a specific calculation:

```bash
docker-compose run poker-calculator python calculator.py
```

You can modify the calculator.py file to change the calculation parameters or write your own scripts.

## Advanced Usage

### Using GPU Acceleration

If you have an NVIDIA GPU and the NVIDIA Container Toolkit installed, the application will automatically use GPU acceleration for Monte Carlo simulations.

To verify GPU availability:

```bash
docker-compose run poker-interactive python -c "from utils.parallel import get_computation_device; print(f'Using: {get_computation_device()}')"
```

### Customizing the Docker Environment

You can create a `.env` file to customize the Docker build process:

```bash
# Example .env file
PYTHON_VERSION=3.9
ITERATIONS=200000
```

### Building Without Docker Compose

If you prefer to use Docker directly:

```bash
# Build the image
docker build -t texas-holdem-calculator .

# Run the tests
docker run --name calculator-test -v $(pwd)/data:/app/data texas-holdem-calculator --test

# Run in interactive mode
docker run -it --rm -v $(pwd)/data:/app/data --entrypoint /bin/bash texas-holdem-calculator
```

## Troubleshooting

### Common Issues

1. **Permission issues with data volume**:
   - Run `chmod -R 777 data/` to ensure the container has write access to the data directory.

2. **GPU not detected**:
   - Verify NVIDIA drivers and container toolkit are installed correctly.
   - Run `nvidia-smi` to check if your GPU is accessible.

3. **Package installation fails**:
   - Try rebuilding without cache: `docker-compose build --no-cache`

### Getting Help

If you encounter any issues not covered here, please open an issue on the GitHub repository. 