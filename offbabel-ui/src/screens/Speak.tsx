import { useEffect, useRef, useState, type FormEvent } from "react"
import { ArrowLeft, ArrowRight, HelpCircle, Mic, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Presence } from "@/components/Presence"
import { LanguageToggle } from "@/components/LanguageToggle"
import { LANGS, type Bubble, type Correction, type Lang, type Presence as PresenceState, type Scenario } from "@/lib/offbabel"

export function Speak({
  presence,
  lang,
  onLang,
  scenario,
  scenarios,
  hits,
  transcript,
  correction,
  onSelectScenario,
  onBack,
  onSend,
  onPtt,
  onHelp,
}: {
  presence: PresenceState
  lang: Lang
  onLang: (l: Lang) => void
  scenario: Scenario
  scenarios: Scenario[]
  hits: number
  transcript: Bubble[]
  correction: Correction | null
  onSelectScenario: (s: Scenario) => void
  onBack: () => void
  onSend: (text: string) => void
  onPtt: (active: boolean) => void
  onHelp: () => void
}) {
  const [text, setText] = useState("")
  const total = scenario.targets.length
  const langLabel = LANGS.find((l) => l.value === lang)?.label ?? "your language"

  const scrollRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [transcript])

  const submit = (e: FormEvent) => {
    e.preventDefault()
    const t = text.trim()
    if (!t) return
    onSend(t)
    setText("")
  }

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col py-5">
      <div className="flex items-center justify-between">
        <Button variant="ghost" className="gap-1.5" onClick={onBack}>
          <ArrowLeft className="size-5" /> Back
        </Button>
        <LanguageToggle value={lang} onChange={onLang} />
      </div>

      {/* Reachy is the focus; the screen is the companion */}
      <div className="mt-1 flex flex-col items-center gap-2">
        <Presence state={presence} size={104} />
        <div className="flex items-center gap-2">
          <span className="text-base font-semibold">{scenario.title}</span>
          <span className="rounded-full bg-info/10 px-2 py-0.5 text-xs font-semibold text-info">
            {scenario.level}
          </span>
        </div>
        <div className="flex items-center gap-1.5" title={`${hits} of ${total} goals`}>
          {scenario.targets.map((t, i) => (
            <span
              key={t}
              className={"size-2.5 rounded-full transition " + (i < hits ? "bg-success" : "bg-border")}
            />
          ))}
          <span className="ml-1 text-xs text-muted-foreground">{hits}/{total} goals</span>
        </div>
      </div>

      {/* Conversation: captions, large and glanceable */}
      <div ref={scrollRef} className="mt-4 flex min-h-0 flex-1 flex-col overflow-y-auto rounded-2xl border bg-card p-4">
        {transcript.length === 0 ? (
          <div className="m-auto max-w-sm text-center text-muted-foreground">
            <p className="text-lg font-medium text-foreground">Talking to Reachy</p>
            <p className="mt-1">
              Hold the button and speak, or type. Reachy replies in {langLabel}, corrects you
              gently, and keeps the conversation going.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {transcript.map((b, i) => (
              <div
                key={i}
                className={
                  b.role === "user"
                    ? "max-w-[80%] self-end rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-primary-foreground"
                    : "max-w-[85%] self-start rounded-2xl rounded-bl-md bg-muted px-4 py-3"
                }
              >
                <div className={b.role === "tutor" ? "text-lg leading-snug" : ""}>{b.text}</div>
                {b.role === "tutor" && b.translation ? (
                  <div className="mt-1.5 border-t border-border/60 pt-1.5 text-sm text-muted-foreground">
                    {b.translation}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>

      {correction && (
        <div className="mt-3 flex flex-wrap items-center gap-2 rounded-xl border border-warning/40 bg-warning/5 px-4 py-3">
          <span className="text-warning line-through decoration-warning/60">{correction.wrong}</span>
          <ArrowRight className="size-4 text-muted-foreground" />
          <span className="font-semibold text-success">{correction.right}</span>
          {correction.note && (
            <span className="w-full text-sm text-muted-foreground">{correction.note}</span>
          )}
        </div>
      )}

      {/* Controls: one big primary action, everything else quiet */}
      <div className="mt-4 flex flex-col gap-3">
        <Button
          className="h-16 gap-2 text-lg"
          onMouseDown={() => onPtt(true)}
          onMouseUp={() => onPtt(false)}
          onMouseLeave={() => onPtt(false)}
        >
          <Mic className="size-6" /> Hold to talk
        </Button>
        <div className="flex items-center gap-2">
          <form onSubmit={submit} className="flex flex-1 gap-2">
            <Input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="...or type here"
              className="h-11 text-base"
              aria-label="Type a message"
            />
            <Button type="submit" variant="secondary" className="h-11 gap-1.5">
              <Send className="size-4" /> Send
            </Button>
          </form>
          <Button
            variant="ghost"
            size="sm"
            className="h-11 gap-1.5 whitespace-nowrap text-muted-foreground"
            onClick={onHelp}
          >
            <HelpCircle className="size-4" /> Help
          </Button>
        </div>
        <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
          <span>Lesson</span>
          {scenarios.map((s) => (
            <button
              key={s.id}
              onClick={() => onSelectScenario(s)}
              className={
                "rounded-full px-2 py-0.5 font-medium transition " +
                (s.id === scenario.id ? "bg-foreground text-background" : "hover:text-foreground")
              }
            >
              {s.level}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
