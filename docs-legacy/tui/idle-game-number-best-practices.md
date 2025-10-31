# Idle Game Number System Best Practices

## The Challenge of Exponential Growth

Idle games typically reach astronomical numbers (10^308 and beyond), requiring specialized handling for:
- Performance (rapid calculations)
- Precision (avoiding rounding errors)
- Display (readable formats)
- Comparisons (efficient greater/less than)
- Storage (save file optimization)

## Recommended Approach: Mantissa + Exponent

### Core Implementation

```javascript
// TypeScript/JavaScript example
class IdleNumber {
  mantissa: number;  // 1.234 (kept between 1-10)
  exponent: number;  // Power of 10
  
  constructor(m: number = 0, e: number = 0) {
    this.mantissa = m;
    this.exponent = e;
    this.normalize();
  }
  
  normalize(): void {
    if (this.mantissa === 0) {
      this.exponent = 0;
      return;
    }
    
    // Keep mantissa between 1 and 10
    while (Math.abs(this.mantissa) >= 10) {
      this.mantissa /= 10;
      this.exponent += 1;
    }
    
    while (Math.abs(this.mantissa) < 1) {
      this.mantissa *= 10;
      this.exponent -= 1;
    }
  }
}
```

## Performance Best Practices

### 1. Threshold-Based System
Use native numbers for small values, switch to scientific notation only when needed:

```python
class HybridNumber:
    def __init__(self, value):
        self.use_native = abs(value) < 1e15
        if self.use_native:
            self.native_value = value
        else:
            self.mantissa = # calculate
            self.exponent = # calculate
    
    def add(self, other):
        if self.use_native and other.use_native:
            # Fast native addition
            return HybridNumber(self.native_value + other.native_value)
        else:
            # Fall back to scientific notation
            return self._scientific_add(other)
```

### 2. Logarithmic Operations
For very large numbers, work in log space:

```javascript
class LogNumber {
  log10Value: number;
  
  constructor(value: number) {
    this.log10Value = Math.log10(Math.max(1e-308, value));
  }
  
  multiply(other: LogNumber): LogNumber {
    // Multiplication becomes addition in log space
    const result = new LogNumber(1);
    result.log10Value = this.log10Value + other.log10Value;
    return result;
  }
  
  toNumber(): number {
    return Math.pow(10, this.log10Value);
  }
}
```

### 3. Break-Even Points
Use these library recommendations based on your maximum numbers:

| Max Number | Recommended Approach | Library |
|------------|---------------------|---------|
| < 10^15 | Native int64/float64 | Built-in |
| 10^15 - 10^308 | Mantissa + Exponent | Custom or decimal.js |
| 10^308 - 10^10000 | Extended precision | break_infinity.js |
| > 10^10000 | Logarithmic | break_eternity.js |

## Optimized Operations

### Addition with Early Exit
```rust
fn add_game_numbers(a: &GameNumber, b: &GameNumber) -> GameNumber {
    // Early exit if one number is negligible
    let exp_diff = (a.exponent - b.exponent).abs();
    if exp_diff > 15 {
        return if a.exponent > b.exponent { a.clone() } else { b.clone() };
    }
    
    // Actual addition only when numbers are comparable
    // ...
}
```

### Cached Formatting
```python
class CachedNumber:
    def __init__(self, value):
        self.value = value
        self._formatted_cache = None
        self._cache_precision = None
    
    def format(self, precision=2):
        if self._formatted_cache and self._cache_precision == precision:
            return self._formatted_cache
        
        self._formatted_cache = self._do_format(precision)
        self._cache_precision = precision
        return self._formatted_cache
    
    def invalidate_cache(self):
        self._formatted_cache = None
```

## Display Formatting Strategy

### Suffix System with Smooth Transitions
```typescript
const SUFFIXES = [
  { threshold: 1e3, suffix: "K" },
  { threshold: 1e6, suffix: "M" },
  { threshold: 1e9, suffix: "B" },
  { threshold: 1e12, suffix: "T" },
  // ... up to desired scale
  { threshold: 1e303, suffix: "CTG" }, // Centillion
];

function formatNumber(value: number): string {
  if (value < 1000) return value.toFixed(0);
  
  for (let i = SUFFIXES.length - 1; i >= 0; i--) {
    if (value >= SUFFIXES[i].threshold) {
      const scaled = value / SUFFIXES[i].threshold;
      return scaled.toFixed(2) + SUFFIXES[i].suffix;
    }
  }
  
  // Fallback to scientific notation
  return value.toExponential(2);
}
```

### Mixed Notation System
```python
def format_mixed(number):
    """Use suffixes up to a point, then scientific notation."""
    if number < 1e6:
        return f"{number:,.0f}"  # Comma-separated
    elif number < 1e33:
        return format_with_suffix(number)  # K, M, B, etc.
    elif number < 1e308:
        return f"{number:.2e}"  # Scientific notation
    else:
        return format_logarithmic(number)  # Special handling
```

## Memory Optimization

### Pooling Number Objects
```javascript
class NumberPool {
  private pool: IdleNumber[] = [];
  
  acquire(mantissa: number = 0, exponent: number = 0): IdleNumber {
    if (this.pool.length > 0) {
      const num = this.pool.pop()!;
      num.set(mantissa, exponent);
      return num;
    }
    return new IdleNumber(mantissa, exponent);
  }
  
  release(num: IdleNumber): void {
    if (this.pool.length < 100) {  // Limit pool size
      this.pool.push(num);
    }
  }
}
```

### Immutable vs Mutable Operations
```python
# Immutable (safer, more memory)
def add_immutable(a, b):
    return GameNumber(a.mantissa + b.mantissa, a.exponent)

# Mutable (faster, less memory)
def add_mutable(a, b):
    a.mantissa += b.mantissa
    a.normalize()
    return a

# Best practice: Provide both
class GameNumber:
    def add(self, other):  # Immutable
        result = GameNumber()
        # ... calculation
        return result
    
    def add_in_place(self, other):  # Mutable
        # ... modify self
        return self
```

## Save File Optimization

### Compact Serialization
```json
// Bad: Verbose
{
  "resources": {
    "mantissa": 1.23456789,
    "exponent": 45,
    "formatted": "1.23e45"
  }
}

// Good: Compact
{
  "resources": "1.23456789e45"
}

// Best: Binary format
// Use MessagePack or Protocol Buffers for 50-70% size reduction
```

### Delta Compression for Saves
```python
class SaveManager:
    def create_save_delta(self, current_state, previous_state):
        """Only save changed values."""
        delta = {}
        for key, value in current_state.items():
            if key not in previous_state or previous_state[key] != value:
                delta[key] = value
        return delta
    
    def apply_delta(self, base_state, delta):
        """Reconstruct full state from delta."""
        result = base_state.copy()
        result.update(delta)
        return result
```

## Recommended Libraries by Language

### JavaScript/TypeScript
1. **decimal.js** - General purpose, good to 10^308
2. **break_infinity.js** - Optimized for idle games, handles up to 10^(10^308)
3. **break_eternity.js** - For extreme scales, uses logarithmic representation

### Python
1. **decimal** (built-in) - Arbitrary precision, but slower
2. **mpmath** - Fast arbitrary precision
3. **numpy** with custom dtype - For vectorized operations

### Rust
1. **rust_decimal** - Fast, supports up to 10^28
2. **num-bigint** - Arbitrary precision integers
3. **Custom mantissa+exponent** - Most performant for idle games

### C#/Unity
1. **System.Numerics.BigInteger** - Built-in arbitrary precision
2. **DoubleDouble** - 128-bit precision
3. **Custom implementation** - Based on break_infinity.js

## Performance Benchmarks

### Operations Per Second (Typical)
| Operation | Native Float | Decimal.js | Break_Infinity | Custom M+E |
|-----------|-------------|------------|----------------|------------|
| Addition | 1,000M | 10M | 50M | 100M |
| Multiplication | 1,000M | 8M | 45M | 90M |
| Comparison | 2,000M | 15M | 80M | 150M |
| Formatting | 10M | 2M | 5M | 8M |

## Common Pitfalls to Avoid

### 1. Using BigInt for Everything
BigInt is exact but slow. Reserve for special cases (e.g., premium currency).

### 2. Frequent Normalization
```javascript
// Bad: Normalizes after every operation
number.add(increment).normalize().multiply(multiplier).normalize();

// Good: Batch operations, normalize once
number.addMultiple([increment1, increment2])
      .multiply(multiplier)
      .normalize();
```

### 3. String Parsing for Math
```python
# Bad: Converting to/from strings
result = str(float(str(a)) + float(str(b)))

# Good: Keep numeric representation
result = a.add(b)
```

### 4. Not Caching Expensive Operations
```typescript
// Bad: Recalculates every frame
function render() {
  display.text = formatNumber(calculateTotal());  // Expensive
}

// Good: Cache and invalidate
let cachedTotal: string | null = null;
function render() {
  if (!cachedTotal) {
    cachedTotal = formatNumber(calculateTotal());
  }
  display.text = cachedTotal;
}
```

## Testing Strategies

### Edge Cases to Test
```python
test_cases = [
    0,
    1,
    -1,
    1e-308,  # Minimum positive
    1e308,   # Maximum float
    float('inf'),
    float('-inf'),
    float('nan'),
    1.0000000000001,  # Precision testing
    9.9999999999999,  # Normalization boundary
]
```

### Precision Validation
```javascript
function testPrecision() {
  const a = new GameNumber(1e50);
  const b = new GameNumber(1);
  const result = a.add(b);
  
  // Should maintain the large number
  assert(result.equals(a), "Small addition lost to precision");
  
  // But should work for comparable numbers
  const c = new GameNumber(1e50);
  const d = new GameNumber(2e50);
  const sum = c.add(d);
  assert(sum.equals(new GameNumber(3e50)), "Comparable addition failed");
}
```

## Conclusion

For idle games, the optimal approach is:

1. **Use native numbers below 10^15** for maximum performance
2. **Switch to mantissa+exponent representation** for larger numbers
3. **Implement lazy evaluation** and caching for expensive operations
4. **Format numbers progressively** (commas → suffixes → scientific)
5. **Optimize save files** with compression and delta encoding
6. **Test thoroughly** at boundary conditions

The best implementation depends on your game's specific requirements, but following these patterns will ensure smooth performance even with astronomical numbers.