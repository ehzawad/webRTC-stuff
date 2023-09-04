# coding=utf8

  
 
def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "জিরো", "ওয়ান", "টু", "থ্রি", "ফোর", "ফাইভ", "সিক্স", "সেভেন", "এইট",
        "নাইন", "টেন", "ইলেভেন", "টুয়েলভ", "থার্টিন", "ফোর্টিন", "ফিফটিন",
        "সিক্সটিন", "সেভেনটিন", "এইটটিন", "নাইনটিন",
      ]

      tens = ["", "", "টুয়েন্টি", "থার্টি", "ফরটি", "ফিফটি", "সিক্সটি", "সেভেনটি", "এইটটি", "নাইনটি"]

      scales = ["হান্ড্রেড", "থাউজেন্ড", "মিলি", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)


    current = result = 0
    for word in textnum.split():
        if word in numwords:
          scale, increment = numwords[word]
          current = current * scale + increment
          if scale > 100:
              result += current
              current = 0
    if((result + current)>0):
      return str(result + current)
    else:
      return str(textnum)

def spell_to_int(spell):
    bn_num = ['শূন্য', 'এক', 'দুই', 'তিন', 'চার', 'পাঁচ', 'ছয়', 'সাত', 'আট', 'নয়', 'দশ', 'এগারো', 'বারো', 'তেরো', 'চৌদ্দ', 'পনেরো', 'ষোল', 'সতেরো', 'আঠারো', 'উনিশ','বিশ','একুশ', 'বাইশ', 'তেইশ', 'চব্বিশ', 'পঁচিশ', 'ছাব্বিশ', 'সাতাশ', 'আঠাশ', 'ঊনত্রিশ', 'ত্রিশ', 'একত্রিশ', 'বত্রিশ', 'তেত্রিশ', 'চৌত্রিশ', 'পঁয়ত্রিশ', 'ছত্রিশ', 'সাঁইত্রিশ', 'আটত্রিশ', 'ঊনচল্লিশ','চল্লিশ','একচল্লিশ', 'বিয়াল্লিশ', 'তেতাল্লিশ', 'চুয়াল্লিশ', 'পঁয়তাল্লিশ', 'ছেচল্লিশ', 'সাতচল্লিশ', 'আটচল্লিশ', 'ঊনপঞ্চাশ', 'পঞ্চাশ', 'একান্ন','বাহান্ন', 'তিপ্পান্ন', 'চুয়ান্ন', 'পঞ্চান্ন', 'ছাপ্পান্ন', 'সাতান্ন', 'আটান্ন', 'ঊনষাট','ষাট','একষট্টি', 'বাষট্টি', 'তেষট্টি', 'চৌষট্টি', 'পঁয়ষট্টি', 'ছেষট্টি', 'সাতষট্টি', 'আটষট্টি', 'ঊনসত্তর', 'সত্তর', 'একাত্তর','বাহাত্তর', 'তিয়াত্তর', 'চুয়াত্তর', 'পঁচাত্তর', 'ছিয়াত্তর', 'সাতাত্তর', 'আটাত্তর', 'ঊনআশি','আশি','একাশি', 'বিরাশি', 'তিরাশি', 'চুরাশি','পঁচাশি', 'ছিয়াশি', 'সাতাশি', 'আটাশি', 'ঊননব্বই', 'নব্বই', 'একানব্বই','বিরানব্বই', 'তিরানব্বই', 'চুরানব্বই', 'পঁচানব্বই', 'ছিয়ানব্বই', 'সাতানব্বই', 'আটানব্বই', 'নিরানব্বই']
    positional= ['কোটি','লক্ষ','হাজার','শত','লাখ']
    positional_dict={'শত':2,'হাজার':3,'লক্ষ':5,'কোটি':7, 'লাখ':5}
    hundreds=['একশ','দুইশ','তিনশ','চারশ','পাঁচশ','ছয়শ','সাতশ','আটশ','নয়শ','দশশ','এগারশো','বারোশো','তেরোশো','চদ্দশো','পনেরোশো','ষোলশো','সতেরোশো','আঠারশো','উনিশশো']
    hundreds_synonyms=[['একশ'],['দুইশ'],['তিনশ'],['চারশ'],['পাঁচশ'],['ছয়শ'],['সাতশ'],['আটশ'],['নয়শ'],['দশশ'],['এগারশো'],['বাবোশো','বারোশো'],['তেরোশো'],['চদ্দশো'],['পনেরোশো'],['ষোলশো'],['সতেরোশো'],['আঠারশো'],['উনিশশো']]
    bn_num_dict={}
    all_kWords=[]
    all_kWords.extend(positional)
    all_kWords.extend(hundreds)
    all_kWords.extend(bn_num)

    for i in range(len(bn_num)):
        bn_num_dict[bn_num[i]]=i
    
    hundreds_dict={}
    for i in range(len(hundreds)):
        hundreds_dict[hundreds[i]]=(i+1)*100
    
    input_string = spell.split()
    input_spelling = []
    for i in input_string:
        if i not in all_kWords:
            continue
        input_spelling.append(i)

    num=0
    if len(input_spelling)==0:
        return spell

    for i in range(len(input_spelling)):
        if len(input_spelling)==1:
            if input_spelling[i] in bn_num:
                num=bn_num_dict[input_spelling[i]]
            else :
                if input_spelling[i] in hundreds_dict:
                    num=hundreds_dict[input_spelling[i]]
                else:
                    for ii in range(len(hundreds_synonyms)):
                        if input_spelling[i] in hundreds_synonyms[ii]:
                            num=(ii+1)*100 
        else:
            if input_spelling[i] in positional and i!=len(input_spelling)-1:
                num+=bn_num_dict[input_spelling[i-1]]*10**positional_dict[input_spelling[i]]
            if input_spelling[i] in hundreds and i!=len(input_spelling)-1:
                if input_spelling[i] in hundreds_dict:
                    num+=hundreds_dict[input_spelling[i]]
                else:
                    for ii in range(len(hundreds_synonyms)):
                        if input_spelling[i] in hundreds_synonyms[ii]:
                            num+=(ii+1)*100
                    
            if i==len(input_spelling)-1 and input_spelling[i] not in positional:
                if input_spelling[i] in bn_num:
                    num+=bn_num_dict[input_spelling[i]]
                else :
                    if input_spelling[i] in hundreds_dict:
                        num+=hundreds_dict[input_spelling[i]]
                    else:
                        for ii in range(len(hundreds_synonyms)):
                            if input_spelling[i] in hundreds_synonyms[ii]:
                                num+=(ii+1)*100
            if input_spelling[i] in positional and i==len(input_spelling)-1:
                if input_spelling[i-1] in bn_num_dict:
                	num+=bn_num_dict[input_spelling[i-1]]
                	num=num*10**positional_dict[input_spelling[i]]
            # else:
            #     num = num*10**positional_dict[input_spelling[i]]
    return str(num)
