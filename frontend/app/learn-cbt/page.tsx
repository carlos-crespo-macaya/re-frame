'use client'

import Link from 'next/link'

export default function LearnCBT() {
  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <Link href="/" className="inline-block">
                <h1 className="text-2xl font-heading font-semibold text-brand-green-400 hover:text-brand-green-300 transition-colors">
                  re-frame
                </h1>
              </Link>
              <p className="text-sm text-[#999999] mt-1">
                Cognitive reframing support
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="container-safe py-8 md:py-12">
          <article className="max-w-3xl mx-auto">
            <h1 className="text-[32px] font-semibold text-[#EDEDED] mb-8">
              What is CBT?
            </h1>
            
            <p className="text-base text-[#999999] leading-relaxed mb-6">
              Cognitive Behavioural Therapy (CBT) is an evidence-based approach that links <strong className="text-[#EDEDED]">thoughts, feelings, and actions</strong> <sup className="text-xs"><a href="#ref1" className="text-brand-green-400 hover:text-brand-green-300">[1]</a></sup>. By spotting common <strong className="text-[#EDEDED]">thinking traps</strong>—such as catastrophising, mind-reading, or &ldquo;all-or-nothing&rdquo; statements—you can practise kinder, more balanced perspectives.
            </p>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              Why it helps with AvPD
            </h2>
            
            <p className="text-base text-[#999999] leading-relaxed mb-4">
              People living with Avoidant Personality Disorder often battle intense self-criticism and fear of negative evaluation <sup className="text-xs"><a href="#ref2" className="text-brand-green-400 hover:text-brand-green-300">[2]</a></sup>. CBT offers practical tools to:
            </p>

            <ul className="list-disc list-inside space-y-2 text-[#999999] mb-6 pl-4">
              <li><strong className="text-[#EDEDED]">Name</strong> unhelpful thoughts rather than accept them as facts.</li>
              <li><strong className="text-[#EDEDED]">Test</strong> those thoughts against real-world evidence.</li>
              <li><strong className="text-[#EDEDED]">Practise</strong> alternative interpretations in small, safe steps <sup className="text-xs"><a href="#ref3" className="text-brand-green-400 hover:text-brand-green-300">[3]</a></sup>.</li>
            </ul>

            <p className="text-base text-[#999999] leading-relaxed mb-6">
              Consistent CBT exercises can gradually chip away at the belief <em>&ldquo;I will always be rejected.&rdquo;</em>
            </p>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              How re-frame uses CBT
            </h2>
            
            <p className="text-base text-[#999999] leading-relaxed mb-6">
              When you describe a situation, <strong className="text-[#EDEDED]">re-frame</strong> highlights likely thinking traps and suggests gentler viewpoints. You remain in control—choose what feels true and helpful, discard the rest.
            </p>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              Further reading
            </h2>

            <ul className="space-y-2 text-[#999999] mb-8">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">CBT Basics</strong> – Anxiety UK • 
                  <a href="https://www.anxietyuk.org.uk/get-help/resources/" className="text-brand-green-400 hover:text-brand-green-300 underline" target="_blank" rel="noopener noreferrer">
                    Resource page ↗
                  </a>
                </div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">&ldquo;Unhelpful Thinking Styles&rdquo;</strong> factsheet – CCI • 
                  <a href="https://www.cci.health.wa.gov.au/~/media/CCI/Mental-Health-Professionals/Depression/Depression---Information-Sheets/Depression-Information-Sheet---11--Unhelpful-Thinking-Styles.pdf" className="text-brand-green-400 hover:text-brand-green-300 underline" target="_blank" rel="noopener noreferrer">
                    <span className="inline-flex items-center gap-1">
                      <svg className="inline w-[14px] h-[14px]" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M10 9H9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      PDF (200 KB) ↗
                    </span>
                  </a>
                </div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">Avoidant Personality: CBT Workbook</strong> – Psychology Tools • 
                  <a href="https://www.psychologytools.com/professional/problems/personality-disorders#cluster-c-avoidant-personality-disorder" className="text-brand-green-400 hover:text-brand-green-300 underline" target="_blank" rel="noopener noreferrer">
                    Sign in & download ↗
                  </a>
                </div>
              </li>
            </ul>

            <div className="mt-8 p-6 bg-[#2a2a2a] border border-[#3a3a3a] rounded-lg">
              <p className="text-sm text-[#999999] leading-relaxed">
                <strong className="text-[#EDEDED]">Reminder:</strong> re-frame is a self-help companion, not a substitute for professional care.
                If you feel unsafe with your thoughts, please reach out to a qualified therapist or crisis line.
              </p>
            </div>

            <hr className="my-8 border-[#3a3a3a]" />

            <h3 className="text-xl font-semibold text-[#EDEDED] mb-4">
              References
            </h3>

            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b border-[#3a3a3a]">
                    <th className="text-left py-2 pr-4 text-[#EDEDED] font-semibold">#</th>
                    <th className="text-left py-2 pr-4 text-[#EDEDED] font-semibold">Source</th>
                    <th className="text-left py-2 text-[#EDEDED] font-semibold">Key Point Supported</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-[#2a2a2a]">
                    <td className="py-3 pr-4 text-[#999999] align-top" id="ref1">[1]</td>
                    <td className="py-3 pr-4 text-[#999999]">
                      Beck, A.T. <em>Cognitive Therapy and the Emotional Disorders.</em><br />
                      International Universities Press, 1976.
                    </td>
                    <td className="py-3 text-[#999999]">Definition of CBT & thought–emotion–behaviour link</td>
                  </tr>
                  <tr className="border-b border-[#2a2a2a]">
                    <td className="py-3 pr-4 text-[#999999] align-top" id="ref2">[2]</td>
                    <td className="py-3 pr-4 text-[#999999]">
                      Lampe, L., & Sunderland, M. (2013). <em>Avoidant Personality Disorder: current status and future directions.</em> <strong>Australian & New Zealand Journal of Psychiatry, 47(6)</strong>, 515-22.
                    </td>
                    <td className="py-3 text-[#999999]">AvPD features: fear of evaluation, self-criticism</td>
                  </tr>
                  <tr>
                    <td className="py-3 pr-4 text-[#999999] align-top" id="ref3">[3]</td>
                    <td className="py-3 pr-4 text-[#999999]">
                      Clark, D.A. & Beck, A.T. <em>Cognitive Therapy of Anxiety Disorders.</em><br />
                      The Guilford Press, 2010.
                    </td>
                    <td className="py-3 text-[#999999]">CBT techniques: naming, testing, practising alternatives</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="mt-6 p-4 bg-[#2a2a2a] border border-[#3a3a3a] rounded-lg">
              <p className="text-xs text-[#999999] leading-relaxed">
                <strong>Note:</strong> CCI&apos;s &ldquo;Unhelpful Thinking Styles&rdquo; PDF and Psychology Tools workbooks are freely available, evidence-aligned handouts often recommended by clinicians.<br />
                Link to CCI module: <a href="https://www.cci.health.wa.gov.au/Resources/Looking-After-Yourself/Unhelpful-Thinking-Styles" className="text-brand-green-400 hover:text-brand-green-300 underline break-words" target="_blank" rel="noopener noreferrer">https://www.cci.health.wa.gov.au/Resources/Looking-After-Yourself/Unhelpful-Thinking-Styles</a>
              </p>
            </div>

            <div className="mt-8 text-center">
              <Link href="/" className="inline-flex items-center gap-2 text-brand-green-400 hover:text-brand-green-300 underline">
                ← Return to re-frame
              </Link>
            </div>
          </article>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#3a3a3a]">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-400">
              re-frame
            </h2>
            <p className="text-xs text-[#999999]">
              © 2024 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}