import { ThemeToggle } from '@/components/ui'

export default function LearnCBT() {
  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-ui-bg-100 to-transparent dark:from-ui-bg-900 dark:to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <a href="/" className="inline-block">
                <h1 className="text-2xl font-heading font-semibold text-brand-green-700 dark:text-brand-green-400">
                  re-frame
                </h1>
              </a>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                Cognitive reframing support
              </p>
            </div>
            <ThemeToggle className="ml-4" />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main id="main-content" className="flex-1">
        <div className="container-safe py-8 md:py-12">
          <article className="max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-heading font-medium text-neutral-800 dark:text-neutral-100 mb-8">
              What is CBT?
            </h2>
            
            <div className="prose prose-neutral dark:prose-invert max-w-none space-y-6">
              <p className="text-lg text-neutral-600 dark:text-neutral-300 leading-relaxed">
                <strong>Cognitive Behavioural Therapy (CBT)</strong> is an evidence-based mental health practice that focuses on the relationships between thoughts, feelings, and behaviours.
              </p>

              <p className="text-base text-neutral-600 dark:text-neutral-300">
                CBT operates on a simple principle: our thoughts influence our emotions and actions. When we experience distressing situations, we often develop patterns of thinking that may not reflect reality accurately. These &ldquo;thinking traps&rdquo; or &ldquo;cognitive distortions&rdquo; can lead to unnecessary suffering.
              </p>

              <div className="my-8 p-6 bg-ui-bg-50 dark:bg-ui-bg-900 border border-ui-border-light dark:border-ui-border-dark rounded-xl">
                <h3 className="text-xl font-heading font-medium text-neutral-800 dark:text-neutral-100 mb-4">
                  How re-frame uses CBT
                </h3>
                <p className="text-base text-neutral-600 dark:text-neutral-300">
                  When you share a thought with re-frame, we identify potential thinking patterns and offer alternative perspectives based on established CBT techniques. We&apos;re not replacing therapy – we&apos;re providing a tool to practice cognitive reframing in your daily life.
                </p>
              </div>

              <h3 className="text-2xl font-heading font-medium text-neutral-800 dark:text-neutral-100 mt-10 mb-4">
                Common thinking patterns
              </h3>
              
              <ul className="space-y-4">
                <li className="pl-6 relative">
                  <span className="absolute left-0 top-1 text-brand-green-600 dark:text-brand-green-400">•</span>
                  <strong className="text-neutral-800 dark:text-neutral-100">All-or-nothing thinking:</strong>
                  <span className="text-neutral-600 dark:text-neutral-300"> Seeing things in black and white terms</span>
                </li>
                <li className="pl-6 relative">
                  <span className="absolute left-0 top-1 text-brand-green-600 dark:text-brand-green-400">•</span>
                  <strong className="text-neutral-800 dark:text-neutral-100">Mind reading:</strong>
                  <span className="text-neutral-600 dark:text-neutral-300"> Assuming we know what others are thinking</span>
                </li>
                <li className="pl-6 relative">
                  <span className="absolute left-0 top-1 text-brand-green-600 dark:text-brand-green-400">•</span>
                  <strong className="text-neutral-800 dark:text-neutral-100">Catastrophizing:</strong>
                  <span className="text-neutral-600 dark:text-neutral-300"> Expecting the worst possible outcome</span>
                </li>
                <li className="pl-6 relative">
                  <span className="absolute left-0 top-1 text-brand-green-600 dark:text-brand-green-400">•</span>
                  <strong className="text-neutral-800 dark:text-neutral-100">Personalization:</strong>
                  <span className="text-neutral-600 dark:text-neutral-300"> Taking responsibility for things outside our control</span>
                </li>
              </ul>

              <p className="text-base text-neutral-600 dark:text-neutral-300 mt-8">
                CBT helps us recognize these patterns and develop more balanced, realistic perspectives. It&apos;s not about &ldquo;positive thinking&rdquo; – it&apos;s about accurate thinking that reflects the full picture of our experiences.
              </p>

              <div className="mt-12 text-center">
                <a 
                  href="/" 
                  className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-brand-green-600 hover:bg-brand-green-700 dark:bg-brand-green-500 dark:hover:bg-brand-green-600 rounded-lg transition-colors duration-200"
                >
                  Try re-frame now
                </a>
              </div>
            </div>
          </article>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-ui-border-light dark:border-ui-border-dark">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-700 dark:text-brand-green-400">
              re-frame
            </h2>
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-brand-green-600 dark:hover:text-brand-green-400 transition-colors"
                  >
                    Privacy
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-brand-green-600 dark:hover:text-brand-green-400 transition-colors"
                  >
                    Support
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-brand-green-600 dark:hover:text-brand-green-400 transition-colors"
                  >
                    About
                  </a>
                </li>
              </ul>
            </nav>
            <p className="text-xs text-neutral-500 dark:text-neutral-500">
              © 2024 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}