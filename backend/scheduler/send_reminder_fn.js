// InsForge Edge Function: send-reminder
// Accepts POST { to, student_name, assignment_title, deadline_str, days_remaining, classroom_link }
// Uses InsForge's internal email via auth send-notification endpoint

export default async function(req: Request): Promise<Response> {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  let body: any;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON body' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  const { to, student_name, assignment_title, deadline_str, days_remaining, classroom_link } = body;

  if (!to || !assignment_title) {
    return new Response(JSON.stringify({ error: 'to and assignment_title are required' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }

  const daysLabel = days_remaining === 0
    ? 'Due TODAY'
    : `${days_remaining} day${days_remaining !== 1 ? 's' : ''} remaining`;

  const subject = days_remaining === 0
    ? `[ClassSync] Due TODAY: ${assignment_title}`
    : `[ClassSync] Reminder: ${assignment_title} – ${daysLabel}`;

  const classroomLine = classroom_link
    ? `\nGoogle Classroom: ${classroom_link}`
    : '';

  const emailBody = `Hi ${student_name || 'Student'},

Your assignment "${assignment_title}" is due soon.

Deadline:  ${deadline_str}
Status:    ${daysLabel}${classroomLine}

Log in to ClassSync to mark it as submitted once you are done.

— ClassSync Team`;

  // Use InsForge's built-in auth email notification endpoint
  const insforgeBase = Deno.env.get('INSFORGE_BASE_URL') || '';
  const anonKey = Deno.env.get('ANON_KEY') || '';

  try {
    const res = await fetch(`${insforgeBase}/api/auth/email/send-notification`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${anonKey}`,
      },
      body: JSON.stringify({
        to,
        subject,
        body: emailBody,
      }),
    });

    const result = await res.json().catch(() => ({}));

    if (!res.ok) {
      return new Response(JSON.stringify({ error: 'Email send failed', detail: result }), {
        status: 502,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
}
