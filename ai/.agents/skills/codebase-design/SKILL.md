---
name: codebase-design
description: Shared terms and rules for designing deep modules. Use this skill to design or improve a module's interface, find ways to deepen modules, choose a seam, improve testing or AI navigation, or provide the deep-module vocabulary to another skill.
---

# Codebase Design

Design **deep modules**. A deep module puts a lot of behaviour behind a small interface. Put the interface at a clear seam. Callers and tests use this interface. Use the terms and rules in this skill when you design or restructure code. Deep modules give callers leverage, help maintainers keep changes local, and make testing easier.

## Glossary

Use these terms as written. Do not replace them with "component", "service", "API", or "boundary". Consistent terms help people discuss the design clearly.

**Module**: Anything with an interface and an implementation. A module can be a function, class, package, or part that spans tiers. Use the term at any scale. _Do not use_: unit, component, service.

**Interface**: Everything a caller must know to use a module correctly. This includes the type signature, rules that must always be true, required order of operations, errors, required configuration, and performance properties. _Do not use_: API or signature. These terms only describe part of the interface.

**Implementation**: The code inside a module. This is different from an **Adapter**. An adapter can have a large implementation, such as a Postgres repository, or a small one, such as an in-memory fake. Use "adapter" when you discuss its role at a seam. Otherwise, use "implementation".

**Depth**: The leverage provided by an interface. It describes how much behaviour a caller or test can use for the amount of interface it must learn. A module is **deep** when a small interface provides access to a lot of behaviour. A module is **shallow** when its interface is nearly as complex as its implementation.

**Seam** _(Michael Feathers)_: A place where you can change behaviour without changing the code at that place. A seam is where a module's interface lives. Choosing a seam is a separate decision from choosing what behaviour belongs behind it. _Do not use_: boundary. This term can mean a DDD bounded context.

**Adapter**: A concrete implementation that meets an interface at a seam. The term describes its role, not its internal details.

**Leverage**: The benefit callers get from depth. A small interface gives callers more capability. One implementation can support many call sites and tests.

**Locality**: The benefit maintainers get from depth. Changes, bugs, knowledge, and checks stay in one place instead of spreading across callers. Fix it once, and the fix applies everywhere.

## Deep vs shallow

**Deep module** = a small interface + a large implementation:

```
┌─────────────────────┐
│   Small Interface   │  <- Few methods, simple parameters
├─────────────────────┤
│                     │
│  Deep Implementation│  <- Complex logic hidden
│                     │
└─────────────────────┘
```

**Shallow module** = a large interface + a small implementation. Avoid this shape:

```
┌─────────────────────────────────┐
│       Large Interface           │  <- Many methods, complex parameters
├─────────────────────────────────┤
│  Thin Implementation            │  <- Just passes through
└─────────────────────────────────┘
```

When you design an interface, ask:

- Can you use fewer methods?
- Can you simplify the parameters?
- Can the module hide more complexity?

## Principles

- **Depth belongs to the interface, not the implementation.** A deep module can contain small parts that can be replaced or mocked. These parts are not part of the module's interface. A module can have **internal seams** inside its implementation for its own tests, and an **external seam** at its interface.
- **The deletion test.** Imagine removing the module. If the complexity goes away, the module only passed work through. If the complexity appears in many callers, the module was useful.
- **The interface is the test surface.** Callers and tests use the same seam. If you need to test past the interface, the module may have the wrong shape.
- **One adapter means a possible seam. Two adapters mean a real seam.** Do not add a seam unless something varies across it.

## Designing for testability

Good interfaces make code easier to test:

1. **Accept dependencies. Do not create them.**

   ```typescript
   // Easier to test
   function processOrder(order, paymentGateway) {}

   // Harder to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Return results. Avoid side effects.**

   ```typescript
   // Easier to test
   function calculateDiscount(cart): Discount {}

   // Harder to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Keep the interface small.** Fewer methods can mean fewer tests. Fewer parameters make test setup simpler.

## Relationships

- A **Module** has one **Interface**. Callers and tests use it.
- **Depth** describes a **Module** in relation to its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and meets the **Interface**.
- **Depth** gives callers **Leverage** and gives maintainers **Locality**.

## Rejected framings

- **Depth as the ratio of implementation lines to interface lines** (Ousterhout): This can reward a large implementation that has been padded with extra code. Use depth as leverage instead.
- **"Interface" means only the TypeScript `interface` keyword or a class's public methods**: This is too narrow. Here, an interface includes every fact a caller must know.
- **"Boundary"**: This term can mean a DDD bounded context. Say **seam** or **interface** instead.

## Going deeper

- **To deepen a group of modules given their dependencies**, see [DEEPENING.md](DEEPENING.md). It describes dependency types, seam rules, and how to replace dependencies in tests instead of adding layers.
- **To explore different interfaces**, see [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md). It describes how to use parallel sub-agents to design several different interfaces and compare their depth, locality, and seam placement.
