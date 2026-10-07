# Deepening

Use this guide to deepen a group of shallow modules safely. First, classify the dependencies. This guide uses the terms in [SKILL.md](SKILL.md): **module**, **interface**, **seam**, and **adapter**.

## Dependency categories

When you assess modules for deepening, classify their dependencies. The category determines how to test the deepened module at its seam.

### 1. In-process dependencies

These dependencies use pure computation or in-memory state. They do not perform I/O. You can always deepen these modules: combine them and test through the new interface. You do not need an adapter.

### 2. Dependencies with local test substitutes

These dependencies have local substitutes for tests, such as PGLite for Postgres or an in-memory filesystem. Deepen the modules if the substitute is available. Run the substitute in the test suite and test the deepened module with it. The seam stays inside the module. Do not add a port to the module's external interface.

### 3. Remote services that you own (Ports and Adapters)

These are your services that communicate over a network, such as microservices or internal APIs. Define a **port** (interface) at the seam. Keep the logic in the deep module and inject the transport as an **adapter**. Tests use an in-memory adapter. Production uses an HTTP, gRPC, or queue adapter.

Example recommendation: _"Define a port at the seam. Use an HTTP adapter in production and an in-memory adapter in tests. This keeps the logic in one deep module, even though the service runs across a network."_

### 4. External services that you do not own

These are third-party services that you do not control, such as Stripe or Twilio. Pass the external dependency to the deepened module through an injected port. Tests use a mock adapter.

## Seam discipline

- **One adapter means a possible seam. Two adapters mean a real seam.** Add a port only when at least two adapters are needed, usually one for production and one for tests. One adapter alone adds indirection without a clear benefit.
- **Internal seams and external seams.** A deep module can have internal seams inside its implementation for its own tests. It also has an external seam at its interface. Do not expose internal seams through the interface just because tests use them.

## Testing strategy: replace old tests; do not add layers

- Delete unit tests for the old shallow modules when tests at the deepened module's interface cover their behaviour.
- Write tests through the deepened module's interface. The **interface is the test surface**.
- Check observable results through the interface. Do not check internal state.
- Tests should still pass after internal refactoring because they check behaviour, not implementation. If an implementation change requires a test change, that test reaches past the interface.
