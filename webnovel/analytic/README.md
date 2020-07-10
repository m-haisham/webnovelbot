# Analysers

## Forward Crawl

Calculate while abiding by the rules:

- all chapters must be unlocked continuously
- cheaper chapters with coins
- expensive chapters with fastpass
- chapters unlocked using coins must not exceed `maximum_cost` individually

## Efficient

The only difference between [Forward Crawl](#forward-crawl) and **Efficient**
is that the unlocked chapters wont be continuous

## HardLine

Takes a hard stance and draws two lines. One for coins and another fastpass.

Anything below or equal to coins line is selected for coins. And
anything above or equal to fastpass line is selected for fastpass

That is until provided profile resources are exhausted.
