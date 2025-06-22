// Type definitions for translation keys
// Auto-generated based on the structure of the English translations

export type Messages = {
  common: {
    navigation: {
      home: string;
      about: string;
      'learn-cbt': string;
      support: string;
      privacy: string;
    };
    actions: {
      submit: string;
      cancel: string;
      save: string;
      delete: string;
      edit: string;
      close: string;
      clear: string;
      back: string;
      next: string;
      continue: string;
      start: string;
      finish: string;
      retry: string;
    };
    status: {
      loading: string;
      saving: string;
      processing: string;
      success: string;
      error: string;
      warning: string;
      info: string;
    };
    errors: {
      generic: string;
      network: string;
      validation: string;
      notFound: string;
      unauthorized: string;
      rateLimit: string;
    };
    footer: {
      copyright: string;
      tagline: string;
    };
    language: {
      selectLanguage: string;
      english: string;
      spanish: string;
    };
  };
  home: {
    hero: {
      title: string;
      subtitle: string;
      cta: string;
    };
    intro: {
      heading: string;
      description: string;
      features: {
        private: {
          title: string;
          description: string;
        };
        evidence: {
          title: string;
          description: string;
        };
        supportive: {
          title: string;
          description: string;
        };
      };
    };
    howItWorks: {
      title: string;
      steps: {
        share: {
          number: string;
          title: string;
          description: string;
        };
        receive: {
          number: string;
          title: string;
          description: string;
        };
        practice: {
          number: string;
          title: string;
          description: string;
        };
      };
    };
    benefits: {
      title: string;
      list: string[];
    };
    testimonial: {
      quote: string;
      author: string;
    };
    cta: {
      ready: string;
      button: string;
      learn: string;
      learnMore: string;
    };
  };
  reframe: {
    page: {
      title: string;
      description: string;
    };
    form: {
      thoughtInput: {
        label: string;
        placeholder: string;
        helperText: string;
        ariaLabel: string;
        status: {
          short: string;
          good: string;
          comprehensive: string;
          maximum: string;
        };
      };
      context: {
        label: string;
        placeholder: string;
        helperText: string;
        ariaLabel: string;
      };
      submit: {
        idle: string;
        loading: string;
        disabled: string;
      };
      characterCount: string;
      keyboardShortcut: string;
      validation: {
        required: string;
        tooShort: string;
        tooLong: string;
      };
    };
    response: {
      title: string;
      processing: string;
      frameworks: {
        cbt: string;
        dbt: string;
        act: string;
        stoic: string;
      };
      sections: {
        reframe: string;
        evidence: string;
        action: string;
        reflection: string;
      };
      actions: {
        tryAnother: string;
        save: string;
        share: string;
        feedback: {
          helpful: string;
          notHelpful: string;
        };
      };
    };
    privacy: {
      notice: string;
      anonymous: string;
    };
    tips: {
      title: string;
      list: string[];
    };
    rateLimit: {
      message: string;
      explanation: string;
    };
  };
  errors: {
    '404': {
      title: string;
      description: string;
      action: string;
    };
    '500': {
      title: string;
      description: string;
      action: string;
    };
    offline: {
      title: string;
      description: string;
      action: string;
    };
    form: {
      required: string;
      email: string;
      minLength: string;
      maxLength: string;
      pattern: string;
    };
    api: {
      timeout: string;
      server: string;
      unknown: string;
    };
    boundaries: {
      title: string;
      description: string;
      action: string;
      report: string;
    };
  };
  about: {
    page: {
      title: string;
      subtitle: string;
    };
    mission: {
      title: string;
      content: string;
    };
    approach: {
      title: string;
      values: {
        privacy: {
          title: string;
          description: string;
        };
        evidence: {
          title: string;
          description: string;
        };
        accessible: {
          title: string;
          description: string;
        };
        respectful: {
          title: string;
          description: string;
        };
      };
    };
    story: {
      title: string;
      content: string;
    };
    team: {
      title: string;
      content: string;
    };
    commitment: {
      title: string;
      list: string[];
    };
    contact: {
      title: string;
      content: string;
      email: string;
      feedback: string;
    };
  };
  'learn-cbt': {
    page: {
      title: string;
      subtitle: string;
    };
    intro: {
      title: string;
      content: string;
    };
    howItWorks: {
      title: string;
      description: string;
      cycle: {
        thought: string;
        feeling: string;
        behavior: string;
        result: string;
      };
      breakingCycle: string;
    };
    techniques: {
      title: string;
      list: {
        cognitive: {
          title: string;
          description: string;
        };
        evidence: {
          title: string;
          description: string;
        };
        behavioral: {
          title: string;
          description: string;
        };
        mindfulness: {
          title: string;
          description: string;
        };
      };
    };
    distortions: {
      title: string;
      description: string;
      list: {
        mindReading: {
          title: string;
          description: string;
        };
        catastrophizing: {
          title: string;
          description: string;
        };
        allOrNothing: {
          title: string;
          description: string;
        };
        personalization: {
          title: string;
          description: string;
        };
        filtering: {
          title: string;
          description: string;
        };
      };
    };
    benefits: {
      title: string;
      list: string[];
    };
    gettingStarted: {
      title: string;
      content: string;
      cta: string;
    };
    resources: {
      title: string;
      books: {
        title: string;
        list: string[];
      };
      note: string;
    };
  };
  support: {
    page: {
      title: string;
      subtitle: string;
    };
    crisis: {
      title: string;
      content: string;
      hotlines: {
        title: string;
        us: {
          name: string;
          number: string;
          description: string;
        };
        text: {
          name: string;
          number: string;
          description: string;
        };
        international: {
          name: string;
          link: string;
          description: string;
        };
      };
    };
    therapy: {
      title: string;
      content: string;
      options: {
        inPerson: {
          title: string;
          description: string;
        };
        online: {
          title: string;
          description: string;
        };
        group: {
          title: string;
          description: string;
        };
      };
      findingHelp: {
        title: string;
        tips: string[];
      };
    };
    selfHelp: {
      title: string;
      books: {
        title: string;
        list: Array<{
          title: string;
          author: string;
          description: string;
        }>;
      };
      apps: {
        title: string;
        list: Array<{
          name: string;
          description: string;
        }>;
      };
    };
    community: {
      title: string;
      content: string;
      list: Array<{
        name: string;
        platform: string;
        description: string;
      }>;
    };
    tips: {
      title: string;
      list: string[];
    };
    reminder: {
      title: string;
      content: string;
    };
  };
  privacy: {
    page: {
      title: string;
      subtitle: string;
      lastUpdated: string;
    };
    intro: {
      title: string;
      content: string;
    };
    principles: {
      title: string;
      list: string[];
    };
    dataCollection: {
      title: string;
      anonymous: {
        title: string;
        description: string;
        list: string[];
      };
      temporary: {
        title: string;
        description: string;
        list: string[];
      };
    };
    dataStorage: {
      title: string;
      thoughts: {
        title: string;
        content: string;
      };
      analytics: {
        title: string;
        content: string;
      };
      security: {
        title: string;
        content: string;
      };
    };
    thirdParties: {
      title: string;
      content: string;
      list: Array<{
        name: string;
        purpose: string;
        data: string;
      }>;
    };
    rights: {
      title: string;
      content: string;
      list: string[];
    };
    cookies: {
      title: string;
      content: string;
      list: string[];
    };
    contact: {
      title: string;
      content: string;
      email: string;
    };
    changes: {
      title: string;
      content: string;
    };
    compliance: {
      title: string;
      content: string;
    };
  };
};

// Helper type for useTranslations hook
export type TranslationNamespace = keyof Messages;